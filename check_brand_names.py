import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

from selector.models import CarBrand, CarModel
from django.db.models import Count, Q

# Parāda markas ar modeļiem bez modif., kuru nosaukums atšķiras no rusins.lv
print('=== Markas DB ar modeļiem bez modif. ===')
brands_missing = CarBrand.objects.annotate(
    total=Count('models', distinct=True),
    no_mod=Count('models', filter=Q(models__modifications__isnull=True), distinct=True)
).filter(no_mod__gt=0).order_by('-no_mod')

for b in brands_missing:
    vts = list(b.vehicle_types.values_list('slug', flat=True))
    print(f'  id={b.id} "{b.name}" [{", ".join(vts)}]: {b.no_mod}/{b.total} bez modif.')
    # Izdrukā pirmos 3 modeļus bez modif.
    no_mods = list(CarModel.objects.filter(
        brand=b, modifications__isnull=True
    ).values_list('name', flat=True)[:3])
    for n in no_mods:
        print(f'    - "{n}"')
