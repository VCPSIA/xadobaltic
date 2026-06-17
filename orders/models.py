from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product, ProductVolume
from decimal import Decimal, ROUND_HALF_UP
import uuid


ORDER_STATUS = [
    ('pending', 'Gaida apstiprinājumu'),
    ('confirmed', 'Apstiprināts'),
    ('processing', 'Tiek apstrādāts'),
    ('shipped', 'Nosūtīts'),
    ('delivered', 'Piegādāts'),
    ('cancelled', 'Atcelts'),
]

PAYMENT_METHOD = [
    ('bank', 'Bankas pārskaitījums'),
    ('card', 'Kredītkarte'),
]

PAYMENT_STATUS = [
    ('pending', 'Gaida'),
    ('paid', 'Samaksāts'),
    ('failed', 'Neizdevās'),
    ('refunded', 'Atmaksāts'),
]


class Order(models.Model):
    number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    session_key = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='bank')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address_line1 = models.CharField(max_length=300)
    address_line2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Latvija')
    company = models.CharField(max_length=200, blank=True)
    vat_nr = models.CharField(max_length=50, blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    invoice_number = models.CharField('Rēķina numurs', max_length=30, blank=True)
    invoice_date = models.DateField('Rēķina datums', null=True, blank=True)
    invoice_sent = models.BooleanField('Rēķins nosūtīts', default=False)
    invoice_sent_at = models.DateTimeField('Nosūtīts', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pasūtījums'
        verbose_name_plural = 'Pasūtījumi'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pasūtījums #{self.number}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f'XB{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def shipping_without_vat(self):
        return (self.shipping_cost / Decimal('1.21')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def shipping_vat(self):
        return (self.shipping_cost - self.shipping_without_vat()).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def recalculate(self):
        items = self.items.all()
        self.subtotal = sum(i.line_total_without_vat() for i in items)
        self.vat_amount = sum(i.line_vat() for i in items)
        total_with_vat = sum(i.line_total() for i in items)
        self.total = total_with_vat + self.shipping_cost
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    volume = models.ForeignKey(ProductVolume, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=300)
    volume_label = models.CharField(max_length=50, blank=True)
    sku = models.CharField(max_length=100, blank=True)
    price_with_vat = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Pasūtījuma pozīcija'
        verbose_name_plural = 'Pasūtījuma pozīcijas'

    def __str__(self):
        return f'{self.product_name} x{self.quantity}'

    def price_without_vat(self):
        return (self.price_with_vat / Decimal('1.21')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def line_total(self):
        return (self.price_with_vat * self.quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def line_total_without_vat(self):
        return (self.price_without_vat() * self.quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def line_vat(self):
        return (self.line_total() - self.line_total_without_vat()).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
