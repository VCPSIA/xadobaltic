"""
Moves SUV models from 'Vieglais auto' to 'SUV / Dzips' vehicle type.
Run: venv\Scripts\python.exe classify_suv.py
"""
import re, os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django
django.setup()

from selector.models import CarBrand, CarModel, VehicleType

SUV_PATTERNS = [
    r'\bXC\d+\b',                        # Volvo XC40, XC60, XC90
    r'\bRAV4\b',                          # Toyota RAV4
    r'\b4Runner\b',
    r'\bCX-\d+\b',                        # Mazda CX-3, CX-5, CX-7, CX-9, CX-30, CX-50, CX-60
    r'\bTucson\b',
    r'\bSanta Fe\b',
    r'\bTiguan\b',
    r'\bTouareg\b',
    r'\bQ[2-8]\b',                        # Audi Q2–Q8
    r'\bGLA-Class\b', r'\bGLB-Class\b', r'\bGLC-Class\b',
    r'\bGLE-Class\b', r'\bGLS-Class\b', r'\bGL-Class\b', r'\bGLK-Class\b',
    r'\bG-Class\b',
    r'\bCayenne\b', r'\bMacan\b',
    r'\bOutlander\b', r'\bASX\b', r'\bEclipse Cross\b',
    r'\bQashqai\b', r'\bX-Trail\b', r'\bPathfinder\b', r'\bMurano\b', r'\bJuke\b',
    r'\bSportage\b', r'\bSorento\b',
    r'\bKona\b', r'\bKONA\b',
    r'\bix35\b', r'\bix55\b', r'\bGrand Santa Fe\b', r'\bPalisade\b',
    r'\bForester\b',
    r'\bOutback\b',
    r'\bLand Cruiser\b', r'\bHighlander\b',
    r'\bExplorer\b', r'\bEcoSport\b', r'\bEscape\b',
    r'\bRenegade\b', r'\bCompass\b', r'\bCherokee\b',
    r'\bFreelander\b', r'\bDiscovery\b', r'\bDefender\b',
    r'\bEvoque\b', r'\bVelar\b',
    r'\bX[1-7]\b',                        # BMW X1–X7
    r'\bSX4 S-Cross\b', r'\bXCeed\b',
    r'\bXCross\b',
]

combined = re.compile('|'.join(SUV_PATTERNS), re.IGNORECASE)

vt_auto = VehicleType.objects.get(id=5)   # Vieglais auto
vt_suv  = VehicleType.objects.get(id=2)   # SUV / Dzips

models_qs = CarModel.objects.filter(vehicle_type=vt_auto).select_related('brand')

moved = 0
brands_updated = set()

for m in models_qs:
    if combined.search(m.name):
        m.vehicle_type = vt_suv
        m.save(update_fields=['vehicle_type'])
        if m.brand_id not in brands_updated:
            if not m.brand.vehicle_types.filter(id=vt_suv.id).exists():
                m.brand.vehicle_types.add(vt_suv)
            brands_updated.add(m.brand_id)
        moved += 1

print(f'Pārcelt modeli: {moved}')
print(f'Brandiem pievienota SUV kategorija: {len(brands_updated)}')

# Sanity check
suv_brands = CarBrand.objects.filter(vehicle_types=vt_suv).count()
suv_models = CarModel.objects.filter(vehicle_type=vt_suv).count()
print(f'SUV/Dzips tagad: {suv_brands} markas, {suv_models} modeli')
