import os, django, sys
os.environ["DJANGO_SETTINGS_MODULE"] = "xadobaltic.settings"
sys.path.insert(0, r"C:\Users\USER\xadobaltic")
sys.stdout.reconfigure(encoding="utf-8")
django.setup()
from selector.models import CarModification
m = CarModification.objects.get(pk=60184)
print(f"spec len: {len(m.oil_spec)}")
print(f"spec: {m.oil_spec}")
