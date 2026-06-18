from django.db import models
from django.utils.text import slugify
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP

VAT_RATE = Decimal('0.21')


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True)
    description_lv = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    description_de = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Zīmols'
        verbose_name_plural = 'Zīmoli'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    name_lv = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200, blank=True)
    name_en = models.CharField(max_length=200, blank=True)
    name_de = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text='Bootstrap icon class, piemēram: bi-droplet')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    description_lv = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    description_de = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Kategorija'
        verbose_name_plural = 'Kategorijas'
        ordering = ['order', 'name_lv']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name_lv} > {self.name_lv}'
        return self.name_lv

    def get_name(self, lang='lv'):
        return getattr(self, f'name_{lang}', '') or self.name_lv

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_lv or self.name_en)
        super().save(*args, **kwargs)


class ProductApplication(models.Model):
    name_lv = models.CharField(max_length=150)
    name_ru = models.CharField(max_length=150, blank=True)
    name_en = models.CharField(max_length=150, blank=True)
    name_de = models.CharField(max_length=150, blank=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100, blank=True)
    description_lv = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    description_de = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Pielietojums'
        verbose_name_plural = 'Pielietojumi'
        ordering = ['order', 'name_lv']

    def __str__(self):
        return self.name_lv

    def get_name(self, lang='lv'):
        return getattr(self, f'name_{lang}', '') or self.name_lv

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_lv or self.name_en)
        super().save(*args, **kwargs)


class VehicleType(models.Model):
    name_lv = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100, blank=True)
    name_en = models.CharField(max_length=100, blank=True)
    name_de = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Transportlīdzekļa tips'
        verbose_name_plural = 'Transportlīdzekļu tipi'
        ordering = ['order']

    def __str__(self):
        return self.name_lv



VISCOSITY_CHOICES = [
    ('0W-16', '0W-16'), ('0W-20', '0W-20'), ('0W-30', '0W-30'), ('0W-40', '0W-40'),
    ('5W-20', '5W-20'), ('5W-30', '5W-30'), ('5W-40', '5W-40'), ('5W-50', '5W-50'),
    ('10W-30', '10W-30'), ('10W-40', '10W-40'), ('10W-60', '10W-60'),
    ('15W-40', '15W-40'), ('20W-50', '20W-50'),
    ('', 'Nav piemērojams'),
]


class Product(models.Model):
    name_lv = models.CharField(max_length=300)
    name_ru = models.CharField(max_length=300, blank=True)
    name_en = models.CharField(max_length=300, blank=True)
    name_de = models.CharField(max_length=300, blank=True)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=100, blank=True, verbose_name='Artikuls')
    barcode = models.CharField(max_length=50, blank=True, verbose_name='Svītru kods (EAN/UPC)')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    vehicle_types = models.ManyToManyField(VehicleType, blank=True, related_name='products')
    applications = models.ManyToManyField('ProductApplication', blank=True, related_name='products')
    nav_subcategory = models.ForeignKey(
        'core.NavCategory',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='products',
        verbose_name='Apakškategorija (navigācija)',
        limit_choices_to={'parent__isnull': False},
    )
    tab_passenger_cars = models.BooleanField(default=False, verbose_name='Automašīnas')
    tab_motorcycle = models.BooleanField(default=False, verbose_name='Mototehnika')
    tab_heavy_truckbus = models.BooleanField(default=False, verbose_name='Kravas automašīnas un cita tehnika')
    tab_ieroci = models.BooleanField(default=False, verbose_name='Ieroči')
    description_lv = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    description_de = models.TextField(blank=True)
    short_description_lv = models.TextField(blank=True)
    short_description_ru = models.TextField(blank=True)
    short_description_en = models.TextField(blank=True)
    short_description_de = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True)
    image2 = models.ImageField(upload_to='products/', blank=True)
    image3 = models.ImageField(upload_to='products/', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_old = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volume_ml = models.PositiveIntegerField(null=True, blank=True, verbose_name='Tilpums (ml)')
    viscosity = models.CharField(max_length=20, choices=VISCOSITY_CHOICES, blank=True)
    specifications_lv = models.TextField(blank=True, help_text='API, ACEA u.c. specifikācijas', verbose_name='Specifikācijas LV')
    specifications_ru = models.TextField(blank=True, verbose_name='Specifikācijas RU')
    specifications_en = models.TextField(blank=True, verbose_name='Specifikācijas EN')
    specifications_de = models.TextField(blank=True, verbose_name='Specifikācijas DE')
    technical_info_lv = models.TextField(blank=True, verbose_name='Tehniskā informācija LV')
    technical_info_ru = models.TextField(blank=True, verbose_name='Tehniskā informācija RU')
    technical_info_en = models.TextField(blank=True, verbose_name='Tehniskā informācija EN')
    technical_info_de = models.TextField(blank=True, verbose_name='Tehniskā informācija DE')
    requirements_lv = models.TextField(blank=True, verbose_name='Prasības LV', help_text='Transportlīdzekļu prasības, standarti')
    requirements_ru = models.TextField(blank=True, verbose_name='Prasības RU')
    requirements_en = models.TextField(blank=True, verbose_name='Prasības EN')
    requirements_de = models.TextField(blank=True, verbose_name='Prasības DE')
    video_url = models.URLField(blank=True, verbose_name='Video URL', help_text='YouTube vai Vimeo saite')
    is_featured = models.BooleanField(default=False, verbose_name='Izceltais produkts')
    is_new = models.BooleanField(default=False, verbose_name='Jaunums')
    is_sale = models.BooleanField(default=False, verbose_name='Izpārdošana')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produkts'
        verbose_name_plural = 'Produkti'
        ordering = ['order', 'name_lv']

    def __str__(self):
        return self.name_lv or self.name_en or self.slug

    @property
    def video_embed_url(self):
        import re
        url = self.video_url
        if not url:
            return ''
        yt = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)', url)
        if yt:
            return f'https://www.youtube.com/embed/{yt.group(1)}'
        vm = re.search(r'vimeo\.com/(\d+)', url)
        if vm:
            return f'https://player.vimeo.com/video/{vm.group(1)}'
        return url

    def get_name(self, lang='lv'):
        return getattr(self, f'name_{lang}', '') or self.name_lv

    def get_description(self, lang='lv'):
        return getattr(self, f'description_{lang}', '') or self.description_lv

    def default_volume(self):
        return self.volumes.filter(is_active=True, is_default=True).first() or self.volumes.filter(is_active=True).first()

    def min_price(self):
        v = self.volumes.filter(is_active=True).order_by('price').first()
        return v.price if v else self.price

    @property
    def main_image(self):
        vol = self.volumes.filter(is_active=True).exclude(image='').order_by('order', 'volume_ml').first()
        if vol and vol.image:
            return vol.image
        return self.image or None

    def discount_percent(self):
        if self.price and self.price_old and self.price_old > self.price:
            return int((1 - self.price / self.price_old) * 100)
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name_lv or self.name_en or 'product')
            slug = base
            n = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Produkta attēls'
        verbose_name_plural = 'Produkta attēli'


class PackagingTemplate(models.Model):
    name = models.CharField('Nosaukums', max_length=100,
                            help_text='Piemēram: 1L kanna, 4L kanna, EX120 blister 6gab')
    auto_apply_to_volume = models.CharField(
        'Automātiski piemērot tilpumam', max_length=10, blank=True,
        help_text='Ja aizpildīts — jauni šī tilpuma ieraksti paņems šos izmērus')
    weight_g = models.PositiveIntegerField('Svars (g)', help_text='Kopā ar iepakojumu')
    length_mm = models.PositiveIntegerField('Garums (mm)')
    width_mm  = models.PositiveIntegerField('Platums (mm)')
    height_mm = models.PositiveIntegerField('Augstums (mm)')
    note = models.CharField('Piezīme', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Iepakojuma šablons'
        verbose_name_plural = 'Iepakojuma šabloni'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} — {self.weight_g}g, {self.length_mm}×{self.width_mm}×{self.height_mm}mm'

    @property
    def volume_cm3(self):
        return round(self.length_mm * self.width_mm * self.height_mm / 1000, 1)


VOLUME_CHOICES = [
    ('8ml',   '8 ml'),
    ('9ml',   '9 ml'),
    ('25ml',  '25 ml'),
    ('250ml', '250 ml'),
    ('320ml', '320 ml'),
    ('400ml', '400 ml'),
    ('500ml', '500 ml'),
    ('0.5L',  '0.5 L'),
    ('1L',    '1 L'),
    ('2L',    '2 L'),
    ('4L',    '4 L'),
    ('5L',    '5 L'),
    ('20L',   '20 L'),
    ('60L',   '60 L'),
    ('200L',  '200 L'),
]

VOLUME_ML = {
    '8ml': 8, '9ml': 9, '25ml': 25, '250ml': 250, '320ml': 320, '400ml': 400, '500ml': 500,
    '0.5L': 500, '1L': 1000, '2L': 2000,
    '4L': 4000, '5L': 5000, '20L': 20000,
    '60L': 60000, '200L': 200000,
}


class ProductVolume(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='volumes')
    label = models.CharField(max_length=10, choices=VOLUME_CHOICES, verbose_name='Tilpums')
    volume_ml = models.PositiveIntegerField(null=True, blank=True, editable=False)
    sku = models.CharField(max_length=100, blank=True, verbose_name='Artikuls')
    barcode = models.CharField(max_length=50, blank=True, verbose_name='Svītru kods')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Cena AR PVN')
    price_old = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Vecā cena AR PVN')
    stock = models.PositiveIntegerField(null=True, blank=True, help_text='Tukšs = neierobežots')
    image = models.ImageField(upload_to='products/volumes/', blank=True, null=True, verbose_name='Foto')
    is_default = models.BooleanField(default=False, verbose_name='Noklusētais tilpums')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    # Iepakojums un piegāde
    packaging = models.ForeignKey(
        PackagingTemplate, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Iepakojuma šablons', related_name='volumes')
    weight_g  = models.PositiveIntegerField('Svars (g)', null=True, blank=True,
                                            help_text='Atstāj tukšu — paņems no šablona')
    length_mm = models.PositiveIntegerField('Garums (mm)', null=True, blank=True)
    width_mm  = models.PositiveIntegerField('Platums (mm)', null=True, blank=True)
    height_mm = models.PositiveIntegerField('Augstums (mm)', null=True, blank=True)

    class Meta:
        verbose_name = 'Tilpums / Cena'
        verbose_name_plural = 'Tilpumi / Cenas'
        ordering = ['order', 'volume_ml', 'price']

    def __str__(self):
        return f'{self.product.name_lv} — {self.label} — {self.price} €'

    def price_without_vat(self):
        return (self.price / Decimal('1.21')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def vat_amount(self):
        return (self.price - self.price_without_vat()).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def discount_percent(self):
        if self.price_old and self.price_old > self.price:
            return int((1 - self.price / self.price_old) * 100)
        return None

    def in_stock(self):
        return self.stock is None or self.stock > 0

    def effective_weight(self):
        return self.weight_g or (self.packaging.weight_g if self.packaging else None)

    def effective_length(self):
        return self.length_mm or (self.packaging.length_mm if self.packaging else None)

    def effective_width(self):
        return self.width_mm or (self.packaging.width_mm if self.packaging else None)

    def effective_height(self):
        return self.height_mm or (self.packaging.height_mm if self.packaging else None)

    def has_shipping_data(self):
        return bool(self.effective_weight() and self.effective_length())

    @property
    def all_images(self):
        imgs = list(self.extra_images.order_by('order'))
        if self.image:
            class _Img:
                def __init__(self, img): self.image = img
                @property
                def url(self): return self.image.url
            imgs.insert(0, _Img(self.image))
        return imgs

    def save(self, *args, **kwargs):
        self.volume_ml = VOLUME_ML.get(self.label)
        # Ja nav šablona — mēģina atrast pēc label
        if not self.packaging_id and self.label:
            tmpl = PackagingTemplate.objects.filter(auto_apply_to_volume=self.label).first()
            if tmpl:
                self.packaging = tmpl
        super().save(*args, **kwargs)


class ProductVolumeImage(models.Model):
    volume = models.ForeignKey(ProductVolume, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='products/volumes/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Tilpuma attēls'
        verbose_name_plural = 'Tilpuma attēli'

    def __str__(self):
        return f'{self.volume} — attēls {self.order}'


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name_lv = models.CharField(max_length=150)
    name_ru = models.CharField(max_length=150, blank=True)
    name_en = models.CharField(max_length=150, blank=True)
    name_de = models.CharField(max_length=150, blank=True)
    value = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Specifikācija'
        verbose_name_plural = 'Specifikācijas'
        ordering = ['order', 'name_lv']

    def __str__(self):
        return f'{self.name_lv}: {self.value}'

    def get_name(self, lang='lv'):
        return getattr(self, f'name_{lang}', '') or self.name_lv


class ProductTechnicalInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='technical_items')
    name_lv = models.CharField('Parametrs', max_length=150)
    name_ru = models.CharField(max_length=150, blank=True)
    name_en = models.CharField(max_length=150, blank=True)
    name_de = models.CharField(max_length=150, blank=True)
    value = models.CharField('Vērtība', max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Tehniskā informācija'
        verbose_name_plural = 'Tehniskā informācija'
        ordering = ['order', 'name_lv']

    def __str__(self):
        return f'{self.name_lv}: {self.value}'

    def get_name(self, lang='lv'):
        return getattr(self, f'name_{lang}', '') or self.name_lv


class ProductRequirement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='requirement_items')
    name_lv = models.CharField('Prasība', max_length=150)
    name_ru = models.CharField(max_length=150, blank=True)
    name_en = models.CharField(max_length=150, blank=True)
    name_de = models.CharField(max_length=150, blank=True)
    value = models.CharField('Vērtība', max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Prasība'
        verbose_name_plural = 'Prasības'
        ordering = ['order', 'name_lv']

    def __str__(self):
        return f'{self.name_lv}: {self.value}'

    def get_name(self, lang='lv'):
        return getattr(self, f'name_{lang}', '') or self.name_lv


class Review(models.Model):
    RATING_CHOICES = [(i, '★' * i) for i in range(1, 6)]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='reviews')
    name = models.CharField('Vārds', max_length=100)
    email = models.EmailField('E-pasts', blank=True)
    rating = models.PositiveSmallIntegerField('Vērtējums', choices=RATING_CHOICES, default=5)
    text = models.TextField('Atsauksme')
    is_approved = models.BooleanField('Apstiprināts', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Atsauksme'
        verbose_name_plural = 'Atsauksmes'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.product.name_lv} ({self.rating}★)'


class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'product')]
        verbose_name = 'Vēlmju saraksts'
        verbose_name_plural = 'Vēlmju saraksti'

    def __str__(self):
        return f'{self.user} — {self.product.name_lv}'
