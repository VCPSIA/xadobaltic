import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

from selector.models import CarBrand, CarModel, CarModification
from catalog.models import VehicleType

# Audi markas
print('=== Audi markas ===')
for b in CarBrand.objects.filter(name__icontains='audi').order_by('name'):
    mcount = CarModel.objects.filter(brand=b).count()
    vts = list(b.vehicle_types.values_list('slug', flat=True))
    print(f'  id={b.id} "{b.name}" - {mcount} modeļi, VTs: {vts}')

# Modelis piemērs - A3 kurā markā?
print('\n=== A3 modeļi ===')
for m in CarModel.objects.filter(name__startswith='A3').order_by('brand__name')[:10]:
    print(f'  id={m.id} "{m.name}" -> brand={m.brand.name} (id={m.brand_id})')

# Kopā modeļi bez markām ar VT1
vt1 = VehicleType.objects.get(slug='passenger-cars')
print('\n=== Markas ar visvairāk modeļiem (top 20) ===')
from django.db.models import Count
for b in CarBrand.objects.annotate(mc=Count('models')).filter(mc__gt=0).order_by('-mc')[:20]:
    vts = list(b.vehicle_types.values_list('slug', flat=True))
    in_vt1 = 'passenger-cars' in vts
    print(f'  id={b.id} "{b.name}": {b.mc} modeļi, VT1={in_vt1}')

# Cik modeļi ir markās BEZ VT1
no_vt1_brands = CarBrand.objects.exclude(vehicle_types=vt1)
no_vt1_models = CarModel.objects.filter(brand__in=no_vt1_brands)
print(f'\nModeļi markās BEZ VT1: {no_vt1_models.count()}')
print('Šīs markas:')
for b in no_vt1_brands.annotate(mc=Count('models')).filter(mc__gt=0).order_by('-mc')[:10]:
    print(f'  "{b.name}": {b.mc} modeļi')
