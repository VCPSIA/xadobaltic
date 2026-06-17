from django.contrib import admin
from .models import CarBrand, CarModel, CarModification, ProductCompatibility


class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 2
    fields = ('name', 'vehicle_type', 'year_from', 'year_to', 'is_active')


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    inlines = [CarModelInline]


class CarModificationInline(admin.TabularInline):
    model = CarModification
    extra = 2
    fields = ('name', 'engine_volume', 'fuel_type', 'power_hp', 'year_from', 'year_to', 'is_active')


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'vehicle_type', 'year_from', 'year_to', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('brand', 'vehicle_type', 'is_active')
    search_fields = ('name', 'brand__name')
    inlines = [CarModificationInline]


@admin.register(CarModification)
class CarModificationAdmin(admin.ModelAdmin):
    list_display = ('car_model', 'name', 'fuel_type', 'year_from', 'year_to', 'is_active')
    list_filter = ('fuel_type', 'is_active', 'car_model__brand')
    search_fields = ('name', 'car_model__name', 'car_model__brand__name')


class ProductCompatibilityInline(admin.TabularInline):
    model = ProductCompatibility
    extra = 1
    autocomplete_fields = ['modification']


@admin.register(ProductCompatibility)
class ProductCompatibilityAdmin(admin.ModelAdmin):
    list_display = ('product', 'modification')
    list_filter = ('modification__car_model__brand',)
    search_fields = ('product__name_lv', 'modification__car_model__name', 'modification__car_model__brand__name')
    autocomplete_fields = ['product', 'modification']
