import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()
from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility

b = CarBrand.objects.get(name='Audi', id=5)
models = CarModel.objects.filter(brand=b, name__icontains='A8').order_by('name')
print(f'=== Audi A8 modeļi ({models.count()} kopā) ===')
for m in models:
    mods = CarModification.objects.filter(car_model=m)
    compat = ProductCompatibility.objects.filter(modification__car_model=m).count()
    print(f'\n  "{m.name}" — {mods.count()} modif., {compat} saderības')
    for mod in mods[:5]:
        print(f'    - {mod.name}')
    if mods.count() > 5:
        print(f'    ... un vēl {mods.count()-5}')
