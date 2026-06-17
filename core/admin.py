from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, Banner, NavCategory, Page


class ColorInput(forms.TextInput):
    input_type = 'color'


class BannerForm(forms.ModelForm):
    title_color = forms.CharField(widget=ColorInput, initial='#ffffff')
    subtitle_color = forms.CharField(widget=ColorInput, initial='#cccccc')
    button_bg_color = forms.CharField(widget=ColorInput, initial='#e30613')

    class Meta:
        model = Banner
        fields = '__all__'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Kontakti', {'fields': ('phone', 'whatsapp', 'viber', 'email')}),
        ('Adrese LV', {'fields': ('address_lv',)}),
        ('Adrese RU', {'fields': ('address_ru',)}),
        ('Adrese EN', {'fields': ('address_en',)}),
        ('Adrese DE', {'fields': ('address_de',)}),
        ('Sociālie tīkli', {'fields': ('facebook', 'instagram', 'youtube')}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    form = BannerForm
    list_display = ('preview_image', 'title_lv', 'order', 'is_active')
    list_display_links = ('title_lv',)
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    fieldsets = (
        ('Attēls', {'fields': ('image', 'image_mobile')}),
        ('Latviski', {'fields': ('title_lv', 'subtitle_lv', 'button_text_lv')}),
        ('Krieviski', {'fields': ('title_ru', 'subtitle_ru', 'button_text_ru'), 'classes': ('collapse',)}),
        ('Angliski', {'fields': ('title_en', 'subtitle_en', 'button_text_en'), 'classes': ('collapse',)}),
        ('Vāciski', {'fields': ('title_de', 'subtitle_de', 'button_text_de'), 'classes': ('collapse',)}),
        ('Teksta dizains', {'fields': ('transition_effect', 'slide_duration', 'image_opacity', 'text_align', 'text_valign', 'font_size', 'font_family', 'title_color', 'subtitle_color', 'button_bg_color')}),
        ('Iestatījumi', {'fields': ('button_url', 'order', 'is_active')}),
    )

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px">', obj.image.url)
        return '-'
    preview_image.short_description = 'Attēls'


@admin.register(NavCategory)
class NavCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_lv', 'tab_slug', 'vehicle_type', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('vehicle_type', 'is_active')
    readonly_fields = ('image_preview',)
    fieldsets = (
        ('Pamatinfo', {'fields': ('parent', 'tab_slug', 'vehicle_type', 'icon', 'image', 'image_preview', 'url', 'order', 'is_active')}),
        ('Nosaukumi', {'fields': ('name_lv', 'name_ru', 'name_en', 'name_de')}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:6px">', obj.image.url)
        return '-'
    image_preview.short_description = 'Priekšskatījums'


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title_lv', 'slug', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('title_lv',)}
    fieldsets = (
        ('URL', {'fields': ('slug', 'is_active')}),
        ('Latviski', {'fields': ('title_lv', 'content_lv', 'meta_description_lv')}),
        ('Krieviski', {'fields': ('title_ru', 'content_ru', 'meta_description_ru'), 'classes': ('collapse',)}),
        ('Angliski', {'fields': ('title_en', 'content_en', 'meta_description_en'), 'classes': ('collapse',)}),
        ('Vāciski', {'fields': ('title_de', 'content_de', 'meta_description_de'), 'classes': ('collapse',)}),
    )
