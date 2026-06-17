from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages as django_messages
from .models import Order, OrderItem
from .invoice import send_invoice_email


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'volume_label', 'sku', 'price_with_vat', 'price_no_vat_display', 'quantity', 'line_total_display')
    fields = readonly_fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def price_no_vat_display(self, obj):
        return f'{obj.price_without_vat()} €'
    price_no_vat_display.short_description = 'Cena bez PVN'

    def line_total_display(self, obj):
        return f'{obj.line_total()} €'
    line_total_display.short_description = 'Rinda kopā'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_form_template = 'admin/orders/order/change_form.html'

    list_display = ('number', 'full_name', 'email', 'total_display', 'status', 'payment_method', 'payment_status', 'invoice_status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'invoice_sent', 'country', 'created_at')
    search_fields = ('number', 'full_name', 'email', 'phone', 'invoice_number')
    readonly_fields = ('number', 'created_at', 'updated_at', 'subtotal', 'vat_amount', 'total', 'invoice_sent', 'invoice_sent_at')
    inlines = [OrderItemInline]
    list_editable = ('status', 'payment_status')

    fieldsets = (
        ('Pasūtījuma info', {
            'fields': ('number', 'status', 'payment_method', 'payment_status', 'created_at', 'updated_at')
        }),
        ('Klients', {
            'fields': ('user', 'full_name', 'email', 'phone', 'company', 'vat_nr')
        }),
        ('Piegādes adrese', {
            'fields': ('address_line1', 'address_line2', 'city', 'postal_code', 'country')
        }),
        ('Summas', {
            'fields': ('subtotal', 'vat_amount', 'shipping_cost', 'total')
        }),
        ('Rēķins', {
            'fields': ('invoice_number', 'invoice_date', 'invoice_sent', 'invoice_sent_at'),
            'description': 'Nospiežot pogu "Izrakstīt rēķinu", rēķins tiks nosūtīts pircējam uz e-pastu.'
        }),
        ('Piezīmes', {
            'fields': ('notes', 'admin_notes')
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:pk>/send-invoice/', self.admin_site.admin_view(self.send_invoice_view), name='order_send_invoice'),
        ]
        return custom + urls

    def send_invoice_view(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if not order.invoice_number:
            year = timezone.now().year
            count = Order.objects.filter(invoice_number__startswith=f'REK-{year}-').count()
            order.invoice_number = f'REK-{year}-{count + 1:04d}'

        order.invoice_date = timezone.now().date()
        order.save(update_fields=['invoice_number', 'invoice_date'])

        try:
            send_invoice_email(order)
            order.invoice_sent = True
            order.invoice_sent_at = timezone.now()
            order.save(update_fields=['invoice_sent', 'invoice_sent_at'])
            django_messages.success(request, f'Rēķins {order.invoice_number} veiksmīgi nosūtīts uz {order.email}')
        except Exception as e:
            django_messages.error(request, f'Kļūda sūtot rēķinu: {e}')

        return redirect(reverse('admin:orders_order_change', args=[pk]))

    def total_display(self, obj):
        return format_html('<strong>{} €</strong>', obj.total)
    total_display.short_description = 'Kopā'

    def invoice_status(self, obj):
        if obj.invoice_sent:
            return format_html('<span style="color:green">✓ {}</span>', obj.invoice_number)
        if obj.invoice_number:
            return format_html('<span style="color:orange">#{}</span>', obj.invoice_number)
        return format_html('<span style="color:#999">—</span>')
    invoice_status.short_description = 'Rēķins'
