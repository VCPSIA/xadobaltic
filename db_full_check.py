import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility
from catalog.models import VehicleType

vt1 = VehicleType.objects.get(slug='passenger-cars')

print('=== KOPĒJIE SKAITI ===')
print(f'Visas markas DB: {CarBrand.objects.count()}')
print(f'Visi modeļi DB: {CarModel.objects.count()}')
print(f'Visas modif. DB: {CarModification.objects.count()}')
print(f'Visas saderības DB: {ProductCompatibility.objects.count()}')

print(f'\nVT1 markas (distinct): {CarBrand.objects.filter(vehicle_types=vt1).distinct().count()}')
print(f'VT1 modeļi (distinct): {CarModel.objects.filter(brand__vehicle_types=vt1).distinct().count()}')
print(f'VT1 modif. (distinct): {CarModification.objects.filter(car_model__brand__vehicle_types=vt1).distinct().count()}')

# Audi EU
try:
    audi = CarBrand.objects.get(name='Audi (EU)')
    print(f'\nAudi EU brand_id: {audi.id}')
    print(f'Audi EU VTs: {list(audi.vehicle_types.values_list("slug", flat=True))}')
    print(f'Audi EU modeļi: {CarModel.objects.filter(brand=audi).count()}')
    no_mods = CarModel.objects.filter(brand=audi, modifications__isnull=True).distinct()
    print(f'Audi EU bez modif.: {no_mods.count()}')
except CarBrand.DoesNotExist:
    print('\nAudi EU - NAV DB!')
    print('Markas ar "Audi":')
    for b in CarBrand.objects.filter(name__icontains='audi'):
        print(f'  {b.id}: {b.name}')

# Modeļi bez modif. pa markām
print('\n=== Top markas ar modeļiem bez modif. ===')
from django.db.models import Count, Q
brands_with_missing = CarBrand.objects.annotate(
    no_mod_count=Count('models', filter=Q(models__modifications__isnull=True))
).filter(no_mod_count__gt=0).order_by('-no_mod_count')[:15]
for b in brands_with_missing:
    print(f'  {b.name}: {b.no_mod_count} bez modif.')
