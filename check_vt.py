import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()
from catalog.models import VehicleType
from selector.models import CarBrand, CarModel, CarModification

print('=== VehicleType saraksts ===')
for vt in VehicleType.objects.all():
    cnt = CarBrand.objects.filter(vehicle_types=vt).count()
    print(f'  id={vt.id} slug="{vt.slug}" name_lv="{vt.name_lv}" -> {cnt} markas')

print('\n=== Audi vehicle_types ===')
b = CarBrand.objects.get(name='Audi', id=5)
for vt in b.vehicle_types.all():
    print(f'  id={vt.id} slug="{vt.slug}"')

print(f'\n=== API test: brands?vehicle_type=<id> ===')
vt = VehicleType.objects.filter(slug='passenger-cars').first()
if vt:
    brands = CarBrand.objects.filter(is_active=True, vehicle_types__id=vt.id).distinct()
    print(f'passenger-cars id={vt.id} -> {brands.count()} markas')
    for b2 in brands[:5]:
        print(f'  {b2.name}')

print('\n=== A8, S8, 4H modifikācijas ===')
from selector.models import CarModel
m = CarModel.objects.filter(name='A8, S8, 4H').first()
if m:
    mods = CarModification.objects.filter(car_model=m, is_active=True)
    print(f'Modeļa id={m.id}, is_active={m.is_active}, {mods.count()} aktīvas modif.')
    for mod in mods[:3]:
        print(f'  id={mod.id} is_active={mod.is_active} "{mod.name}"')
