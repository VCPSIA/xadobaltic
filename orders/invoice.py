from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def send_invoice_email(order):
    seller = getattr(settings, 'SELLER_INFO', {})
    context = {
        'order': order,
        'seller': seller,
        'items': order.items.all(),
    }
    html = render_to_string('emails/invoice.html', context)
    msg = EmailMessage(
        subject=f'Rēķins {order.invoice_number} — XADO Baltic',
        body=html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    msg.content_subtype = 'html'
    msg.send()
