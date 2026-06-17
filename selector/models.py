from django.db import models
from catalog.models import Product, VehicleType


class CarBrand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    lm_id = models.CharField(max_length=32, blank=True, db_index=True, help_text='Liqui-Moly OWW ID')
    logo = models.ImageField(upload_to='car_brands/', blank=True)
    vehicle_types = models.ManyToManyField(VehicleType, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Auto marka'
        verbose_name_plural = 'Auto markas'
        ordering = ['name']

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    lm_id = models.CharField(max_length=32, blank=True, db_index=True, help_text='Liqui-Moly OWW ID')
    lm_category = models.PositiveSmallIntegerField(null=True, blank=True, help_text='LM kategorija: 1=Pkw, 2=Van, 3=LKW, 4=Moto')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, blank=True)
    year_from = models.PositiveIntegerField(null=True, blank=True)
    year_to = models.PositiveIntegerField(null=True, blank=True, help_text='Tukšs = līdz šodienai')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Auto modelis'
        verbose_name_plural = 'Auto modeļi'
        ordering = ['name']

    def __str__(self):
        return f'{self.brand.name} {self.name}'


FUEL_CHOICES = [
    ('gasoline', 'Benzīns'),
    ('diesel', 'Dīzelis'),
    ('hybrid', 'Hibrīds'),
    ('electric', 'Elektriskais'),
    ('lpg', 'LPG'),
    ('other', 'Cits'),
]


class CarModification(models.Model):
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='modifications')
    name = models.CharField(max_length=200, help_text='Piemēram: 2.0 TDI 150hp 2015-2020')
    lm_id = models.CharField(max_length=32, blank=True, db_index=True, help_text='Liqui-Moly OWW ID')
    oil_viscosity = models.CharField(max_length=100, blank=True, help_text='Piemēram: 5W-30, 0W-30')
    oil_spec = models.CharField(max_length=600, blank=True, help_text='OEM apstiprinājumi, piemēram: BMW LL-04, ACEA C3, VW 504.00')
    engine_volume = models.CharField(max_length=20, blank=True, help_text='Piemēram: 2.0')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, blank=True)
    power_hp = models.PositiveIntegerField(null=True, blank=True, verbose_name='Jauda (HP)')
    year_from = models.PositiveIntegerField(null=True, blank=True)
    year_to = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Auto modifikācija'
        verbose_name_plural = 'Auto modifikācijas'
        ordering = ['name']

    def __str__(self):
        return f'{self.car_model} {self.name}'


class ProductCompatibility(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='compatibilities')
    modification = models.ForeignKey(CarModification, on_delete=models.CASCADE, related_name='compatible_products')
    note_lv = models.CharField(max_length=300, blank=True)
    note_ru = models.CharField(max_length=300, blank=True)
    note_en = models.CharField(max_length=300, blank=True)
    note_de = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = 'Produkta saderība'
        verbose_name_plural = 'Produktu saderības'
        unique_together = ('product', 'modification')

    def __str__(self):
        return f'{self.product} → {self.modification}'
