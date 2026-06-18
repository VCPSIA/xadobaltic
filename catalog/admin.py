import json
from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html
from django.db.models import Count
from .models import (Brand, Category, VehicleType, Product, ProductImage,
                     ProductVolume, ProductVolumeImage, ProductSpecification, ProductApplication,
                     ProductTechnicalInfo, ProductRequirement,
                     Review, WishlistItem, PackagingTemplate)

LV = 'Latviski'
RU = 'Krieviski'
EN = 'Angliski'
DE = 'Vāciski'

PRODUCT_LABELS = {
    # Nosaukumi
    'name_lv': 'Nosaukums',
    'name_ru': 'Nosaukums',
    'name_en': 'Name',
    'name_de': 'Name',
    # Īsais apraksts
    'short_description_lv': 'Īsais apraksts',
    'short_description_ru': 'Краткое описание',
    'short_description_en': 'Short description',
    'short_description_de': 'Kurzbeschreibung',
    # Pilnais apraksts
    'description_lv': 'Apraksts',
    'description_ru': 'Описание',
    'description_en': 'Description',
    'description_de': 'Beschreibung',
    # Specifikācijas
    'specifications_lv': 'Specifikācijas',
    'specifications_ru': 'Характеристики',
    'specifications_en': 'Specifications',
    'specifications_de': 'Spezifikationen',
    # Tehniskā informācija
    'technical_info_lv': 'Tehniskā informācija',
    'technical_info_ru': 'Техническая информация',
    'technical_info_en': 'Technical information',
    'technical_info_de': 'Technische Informationen',
    # Prasības
    'requirements_lv': 'Prasības',
    'requirements_ru': 'Требования',
    'requirements_en': 'Requirements',
    'requirements_de': 'Anforderungen',
}


_TINYMCE = TinyMCE()

class ProductAdminForm(forms.ModelForm):
    short_description_lv = forms.CharField(required=False, widget=TinyMCE())
    short_description_ru = forms.CharField(required=False, widget=TinyMCE())
    short_description_en = forms.CharField(required=False, widget=TinyMCE())
    short_description_de = forms.CharField(required=False, widget=TinyMCE())
    description_lv = forms.CharField(required=False, widget=TinyMCE())
    description_ru = forms.CharField(required=False, widget=TinyMCE())
    description_en = forms.CharField(required=False, widget=TinyMCE())
    description_de = forms.CharField(required=False, widget=TinyMCE())

    class Meta:
        model = Product
        fields = '__all__'
        labels = PRODUCT_LABELS


@admin.register(PackagingTemplate)
class PackagingTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'auto_apply_to_volume', 'weight_g', 'dims_display',
                    'volume_cm3_display', 'usage_count')
    list_editable = ('weight_g',)
    search_fields = ('name',)
    fieldsets = (
        ('Nosaukums', {'fields': ('name', 'auto_apply_to_volume', 'note')}),
        ('Izmēri un svars', {
            'fields': ('weight_g', 'length_mm', 'width_mm', 'height_mm'),
            'description': 'Svars — ar iepakojumu. Izmēri — ārējie (mm).'
        }),
    )

    def dims_display(self, obj):
        return f'{obj.length_mm} × {obj.width_mm} × {obj.height_mm} mm'
    dims_display.short_description = 'G × P × A'

    def volume_cm3_display(self, obj):
        return f'{obj.volume_cm3} cm³'
    volume_cm3_display.short_description = 'Tilpums'

    def usage_count(self, obj):
        c = obj.volumes.count()
        return format_html('<span style="color:#e30613;font-weight:600">{}</span>', c) if c else '0'
    usage_count.short_description = 'Izmanto'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Pamata info', {'fields': ('name', 'slug', 'logo', 'order', 'is_active')}),
        ('Apraksts LV', {'fields': ('description_lv',)}),
        ('Apraksts RU', {'fields': ('description_ru',), 'classes': ('collapse',)}),
        ('Apraksts EN', {'fields': ('description_en',), 'classes': ('collapse',)}),
        ('Apraksts DE', {'fields': ('description_de',), 'classes': ('collapse',)}),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:40px">', obj.logo.url)
        return '-'
    logo_preview.short_description = 'Logo'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_lv', 'parent', 'slug', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'parent')
    prepopulated_fields = {'slug': ('name_lv',)}
    fieldsets = (
        ('Pamata info', {'fields': ('slug', 'parent', 'image', 'icon', 'order', 'is_active')}),
        ('Nosaukums LV', {'fields': ('name_lv', 'description_lv')}),
        ('Nosaukums RU', {'fields': ('name_ru', 'description_ru'), 'classes': ('collapse',)}),
        ('Nosaukums EN', {'fields': ('name_en', 'description_en'), 'classes': ('collapse',)}),
        ('Nosaukums DE', {'fields': ('name_de', 'description_de'), 'classes': ('collapse',)}),
    )


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name_lv', 'name_ru', 'name_en', 'name_de', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name_lv',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'alt_text', 'order')


class ProductVolumeInline(admin.TabularInline):
    model = ProductVolume
    extra = 2
    fields = ('label', 'sku', 'barcode', 'price', 'price_old', 'stock', 'image',
              'packaging', 'weight_g', 'length_mm', 'width_mm', 'height_mm',
              'is_default', 'is_active', 'order')
    verbose_name = 'Tilpums / Cena / Iepakojums'
    verbose_name_plural = 'Tilpumi, cenas un iepakojums'

    class Media:
        js = ('admin/js/packaging_autofill.js',)
        css = {'all': ('admin/css/volume_inline.css',)}

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Pielāgojam packaging widget - dropdown ar izmēriem
        return formset


class ProductVolumeImageInline(admin.TabularInline):
    model = ProductVolumeImage
    extra = 5
    fields = ('image', 'alt_text', 'order')
    verbose_name = 'Papildu attēls'
    verbose_name_plural = 'Papildu attēli (min. 5)'


@admin.register(ProductVolume)
class ProductVolumeAdmin(admin.ModelAdmin):
    list_display = ('product', 'label', 'sku', 'price', 'stock', 'is_active')
    list_filter = ('is_active', 'label')
    search_fields = ('product__name_lv', 'sku')
    inlines = [ProductVolumeImageInline]


class _NarrowLangMedia:
    class Media:
        css = {'all': ('admin/css/volume_inline.css',)}


class ProductSpecificationInline(_NarrowLangMedia, admin.TabularInline):
    model = ProductSpecification
    extra = 3
    fields = ('name_lv', 'name_ru', 'name_en', 'name_de', 'value', 'order')
    verbose_name_plural = 'Specifikācijas (tabula)'


class ProductTechnicalInfoInline(_NarrowLangMedia, admin.TabularInline):
    model = ProductTechnicalInfo
    extra = 3
    fields = ('name_lv', 'name_ru', 'name_en', 'name_de', 'value', 'order')
    verbose_name = 'Rinda'
    verbose_name_plural = 'Tehniskā informācija (tabula)'


class ProductRequirementInline(_NarrowLangMedia, admin.TabularInline):
    model = ProductRequirement
    extra = 3
    fields = ('name_lv', 'name_ru', 'name_en', 'name_de', 'value', 'order')
    verbose_name = 'Rinda'
    verbose_name_plural = 'Prasības (tabula)'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    change_form_template = 'admin/catalog/product/change_form.html'

    class Media:
        pass

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'nav_subcategory':
            from core.models import NavCategory
            # Rāda tikai passenger-cars apakškategorijas (identiskas visiem tabiem)
            # Tab piešķiršana notiek caur tab_passenger_cars / tab_heavy_truckbus laukiem
            kwargs['queryset'] = NavCategory.objects.filter(
                parent__isnull=False, tab_slug='passenger-cars'
            ).select_related('parent').order_by('parent__name_lv', 'name_lv')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    filter_horizontal = ('applications', 'vehicle_types')

    list_display = ('image_preview', 'name_lv', 'sku', 'brand', 'category',
                    'price', 'shipping_info', 'is_featured', 'is_new', 'is_sale', 'is_active')
    list_display_links = ('name_lv',)
    list_editable = ('price', 'is_featured', 'is_new', 'is_sale', 'is_active')
    list_filter = ('brand', 'category', 'applications', 'vehicle_types',
                   'is_featured', 'is_new', 'is_sale', 'is_active')
    search_fields = ('name_lv', 'name_ru', 'name_en', 'sku', 'barcode')
    inlines = [ProductVolumeInline, ProductSpecificationInline,
               ProductTechnicalInfoInline, ProductRequirementInline, ProductImageInline]
    fieldsets = (
        ('Pamata info', {'fields': ('slug', 'brand', 'category', 'viscosity')}),
        ('Kategorijas', {'fields': (
            ('tab_passenger_cars', 'tab_motorcycle', 'tab_heavy_truckbus', 'tab_ieroci'),
            'nav_subcategory',
            'applications',
        )}),
        ('Video', {'fields': ('video_url',)}),
        ('Statusi', {'fields': ('is_featured', 'is_new', 'is_sale', 'is_active', 'order')}),
        ('Latviski', {'fields': ('name_lv', 'short_description_lv', 'description_lv'),
                       'classes': ('lang-fs', 'lang-fs-lv')}),
        ('Krieviski', {'fields': ('name_ru', 'short_description_ru', 'description_ru'),
                        'classes': ('lang-fs', 'lang-fs-ru')}),
        ('Angliski', {'fields': ('name_en', 'short_description_en', 'description_en'),
                       'classes': ('lang-fs', 'lang-fs-en')}),
        ('Vāciski', {'fields': ('name_de', 'short_description_de', 'description_de'),
                      'classes': ('lang-fs', 'lang-fs-de')}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px">', obj.image.url)
        return '-'
    image_preview.short_description = 'Foto'

    def shipping_info(self, obj):
        vols = obj.volumes.filter(is_active=True)
        total = vols.count()
        with_data = sum(1 for v in vols if v.has_shipping_data())
        if total == 0:
            return format_html('<span style="color:#999">—</span>')
        if with_data == total:
            return format_html('<span style="color:#28a745">✓ {}/{}</span>', with_data, total)
        return format_html('<span style="color:#ffc107">⚠ {}/{}</span>', with_data, total)
    shipping_info.short_description = 'Piegāde'

    def get_urls(self):
        urls = super().get_urls()
        custom = [path('translate/', self.admin_site.admin_view(self.translate_view), name='catalog_product_translate')]
        return custom + urls

    def translate_view(self, request):
        if request.method != 'POST':
            return JsonResponse({'error': 'POST required'}, status=405)
        try:
            from deep_translator import GoogleTranslator
            text = request.POST.get('text', '').strip()
            target = request.POST.get('target', 'en')
            if not text:
                return JsonResponse({'result': ''})
            result = GoogleTranslator(source='lv', target=target).translate(text)
            return JsonResponse({'result': result or ''})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        templates = list(PackagingTemplate.objects.values(
            'id', 'name', 'weight_g', 'length_mm', 'width_mm', 'height_mm'))
        extra_context['packaging_templates_json'] = json.dumps(templates)
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating_stars', 'is_approved', 'created_at')
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'rating')
    search_fields = ('name', 'text', 'product__name_lv')
    readonly_fields = ('product', 'user', 'name', 'email', 'rating', 'text', 'created_at')
    ordering = ('-created_at',)

    def rating_stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    rating_stars.short_description = 'Vērtējums'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    readonly_fields = ('user', 'product', 'added_at')


@admin.register(ProductApplication)
class ProductApplicationAdmin(admin.ModelAdmin):
    list_display = ('name_lv', 'name_ru', 'name_en', 'slug', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name_lv',)}
    fieldsets = (
        ('Pamata', {'fields': ('slug', 'icon', 'order', 'is_active')}),
        ('Latviski', {'fields': ('name_lv', 'description_lv')}),
        ('Krieviski', {'fields': ('name_ru', 'description_ru'), 'classes': ('collapse',)}),
        ('Angliski', {'fields': ('name_en', 'description_en'), 'classes': ('collapse',)}),
        ('Vāciski', {'fields': ('name_de', 'description_de'), 'classes': ('collapse',)}),
    )
