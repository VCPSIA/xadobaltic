import os, django, sys
os.environ["DJANGO_SETTINGS_MODULE"] = "xadobaltic.settings"
sys.path.insert(0, r"C:\Users\USER\xadobaltic")
sys.stdout.reconfigure(encoding="utf-8")
django.setup()
from selector.models import CarModification
total = CarModification.objects.count()
with_spec = CarModification.objects.exclude(oil_spec="").count()
with_visc = CarModification.objects.exclude(oil_viscosity="").count()
print(f"Kopaa: {total}")
print(f"Ar oil_spec: {with_spec}")
print(f"Ar oil_viscosity: {with_visc}")
bmw = CarModification.objects.filter(car_model__brand__name__icontains="BMW")
bmw_spec = bmw.exclude(oil_spec="").count()
print(f"BMW: {bmw.count()} kopaa, {bmw_spec} ar spec")
ex = bmw.exclude(oil_spec="").first()
if ex:
    print(f"Piemers: {ex.car_model.brand.name} / {ex.car_model.name} / {ex.name}")
    print(f"  visc: {ex.oil_viscosity}")
    print(f"  spec: {ex.oil_spec}")
