from decimal import Decimal, ROUND_HALF_UP
from catalog.models import Product, ProductVolume

CART_SESSION_KEY = 'xado_cart'
VAT_RATE = Decimal('0.21')


class Cart:
    def __init__(self, request):
        self.session = request.session
        self._cart = self.session.setdefault(CART_SESSION_KEY, {})

    def _key(self, product_id, volume_id):
        return f'{product_id}_{volume_id}'

    def add(self, product, volume, quantity=1, override=False):
        key = self._key(product.id, volume.id)
        if key not in self._cart:
            self._cart[key] = {
                'product_id': product.id,
                'volume_id': volume.id,
                'quantity': 0,
                'price': str(volume.price),
                'name': product.name_lv,
                'volume_label': volume.label,
                'sku': volume.sku or product.sku,
            }
        if override:
            self._cart[key]['quantity'] = quantity
        else:
            self._cart[key]['quantity'] += quantity
        if self._cart[key]['quantity'] <= 0:
            del self._cart[key]
        self._save()

    def remove(self, product_id, volume_id):
        key = self._key(product_id, volume_id)
        if key in self._cart:
            del self._cart[key]
            self._save()

    def update(self, product_id, volume_id, quantity):
        key = self._key(product_id, volume_id)
        if key in self._cart:
            if quantity <= 0:
                del self._cart[key]
            else:
                self._cart[key]['quantity'] = quantity
            self._save()

    def _save(self):
        self.session.modified = True

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self._cart = self.session[CART_SESSION_KEY]
        self._save()

    def __iter__(self):
        product_ids = set()
        volume_ids = set()
        for item in self._cart.values():
            product_ids.add(item['product_id'])
            if item['volume_id']:
                volume_ids.add(item['volume_id'])

        products = {p.id: p for p in Product.objects.filter(id__in=product_ids).select_related('brand')}
        volumes = {v.id: v for v in ProductVolume.objects.filter(id__in=volume_ids)}

        for key, item in self._cart.items():
            product = products.get(item['product_id'])
            volume = volumes.get(item['volume_id'])
            if not product or not volume:
                continue
            price = volume.price
            qty = item['quantity']
            price_no_vat = (price / Decimal('1.21')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            line_total = (price * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            line_no_vat = (price_no_vat * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            yield {
                'key': key,
                'product': product,
                'volume': volume,
                'price': price,
                'price_no_vat': price_no_vat,
                'quantity': qty,
                'line_total': line_total,
                'line_no_vat': line_no_vat,
                'line_vat': (line_total - line_no_vat).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            }

    def __len__(self):
        return sum(item['quantity'] for item in self._cart.values())

    def total_with_vat(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self._cart.values()
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def total_without_vat(self):
        total = self.total_with_vat()
        return (total / Decimal('1.21')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def total_vat(self):
        return (self.total_with_vat() - self.total_without_vat()).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def is_empty(self):
        return len(self._cart) == 0
