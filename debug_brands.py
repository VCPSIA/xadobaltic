import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()
from selector.models import CarBrand, CarModel
from django.db.models import Count, Q

print('=== Python filtrēšana ===')
for b in CarBrand.objects.all().order_by('-id'):
    cnt = CarModel.objects.filter(brand=b, modifications__isnull=True).count()
    if cnt > 0:
        print(f'  id={b.id} "{b.name}": {cnt} bez modif.')

print()
print('=== ORM annotācija ===')
qs = CarBrand.objects.annotate(
    no_mod=Count('models', filter=Q(models__modifications__isnull=True), distinct=True)
).filter(no_mod__gt=0).order_by('-no_mod')
for b in qs:
    print(f'  id={b.id} "{b.name}": no_mod={b.no_mod}')
