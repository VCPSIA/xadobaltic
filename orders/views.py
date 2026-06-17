from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm

SHIPPING_COST = Decimal('3.99')
FREE_SHIPPING_THRESHOLD = Decimal('50.00')


def checkout(request):
    cart = Cart(request)
    if cart.is_empty():
        return redirect('cart_detail')

    initial = {}
    if request.user.is_authenticated:
        u = request.user
        p = getattr(u, 'profile', None)
        if p:
            addr = p.get_delivery_address()
            initial = {
                'full_name': p.display_name() if p.is_company() else u.get_full_name(),
                'email': u.email,
                'phone': p.phone,
                'company': p.company_name,
                'vat_nr': p.vat_nr,
                'address_line1': addr['address'],
                'city': addr['city'],
                'postal_code': addr['postal_code'],
                'country': dict(p._meta.get_field('legal_country').choices).get(addr['country'], addr['country']),
            }
        else:
            initial = {'full_name': u.get_full_name(), 'email': u.email}

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            shipping = SHIPPING_COST if cart.total_with_vat() < FREE_SHIPPING_THRESHOLD else Decimal('0')
            order = Order(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address_line1=form.cleaned_data['address_line1'],
                address_line2=form.cleaned_data.get('address_line2', ''),
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                country=form.cleaned_data.get('country', 'Latvija'),
                company=form.cleaned_data.get('company', ''),
                vat_nr=form.cleaned_data.get('vat_nr', ''),
                notes=form.cleaned_data.get('notes', ''),
                payment_method=form.cleaned_data['payment_method'],
                subtotal=cart.total_without_vat(),
                vat_amount=cart.total_vat(),
                shipping_cost=shipping,
                total=cart.total_with_vat() + shipping,
            )
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    volume=item['volume'],
                    product_name=item['product'].name_lv,
                    volume_label=item['volume'].label,
                    sku=item['volume'].sku or item['product'].sku,
                    price_with_vat=item['price'],
                    quantity=item['quantity'],
                )

            cart.clear()
            return redirect('order_success', number=order.number)
    else:
        form = CheckoutForm(initial=initial)

    shipping = SHIPPING_COST if cart.total_with_vat() < FREE_SHIPPING_THRESHOLD else Decimal('0')
    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart,
        'shipping': shipping,
        'total': cart.total_with_vat() + shipping,
        'free_shipping_threshold': FREE_SHIPPING_THRESHOLD,
    })


def order_success(request, number):
    order = get_object_or_404(Order, number=number)
    if order.user and order.user != request.user and not request.user.is_staff:
        if request.session.session_key != order.session_key:
            return redirect('index')
    return render(request, 'orders/order_success.html', {'order': order})
