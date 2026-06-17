import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()
from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility

# Pārbauda VISUS A8 modeļus un to saderību stāvokli
b = CarBrand.objects.get(name='Audi', id=5)
a8_models = CarModel.objects.filter(brand=b, name__icontains='A8').order_by('name')

problems = []
for m in a8_models:
    mods = CarModification.objects.filter(car_model=m, is_active=True)
    for mod in mods:
        cnt = ProductCompatibility.objects.filter(modification=mod).count()
        if cnt == 0:
            problems.append(f'  "{m.name}" / "{mod.name}" → 0 saderības!')

if problems:
    print('=== Modifikācijas BEZ saderībām ===')
    for p in problems:
        print(p)
else:
    print('Visām modifikācijām ir saderības ✓')

# Arī pārbauda vai pastāv duplikāti
print('\n=== Iespējamie duplikāti (vienāds ģenerācija) ===')
seen = {}
for m in a8_models:
    gen = m.name.replace('A8, ', '').replace('A8L, ', '').replace('S8, ', '').replace('S8L, ', '').strip()
    # Ekstrakt chassis code
    import re
    chassis = re.search(r'4[A-Z0-9]+', m.name)
    if chassis:
        code = chassis.group(0)
        if code in seen:
            print(f'  DUPLIKĀTS: "{seen[code]}" un "{m.name}"')
        else:
            seen[code] = m.name
