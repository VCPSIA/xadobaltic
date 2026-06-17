from django.conf import settings
from catalog.models import Category, Brand
from .models import SiteSettings


def site_context(request):
    return {
        'main_categories': Category.objects.filter(is_active=True, parent=None).prefetch_related('children')[:10],
        'site_settings': SiteSettings.get(),
        'SITE_URL': getattr(settings, 'SITE_URL', ''),
        'footer_brands': Brand.objects.filter(is_active=True).order_by('name'),
    }
