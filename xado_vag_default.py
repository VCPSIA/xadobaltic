"""
Uzstāda noklusējuma compat ierakstus VAG (Audi/VW/Skoda/Seat) modifikācijām bez datiem.
- >=2004: 5W-30 504/507 (VW 504.00/507.00 spec)
- <2004 vai bez gada: 5W-40 502.00 (vecāks VAG spec)
Izlaiž modifikācijas, kurām jau ir compat ieraksti.
"""
import os, sys, re
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from selector.models import CarBrand, CarModification, ProductCompatibility
from catalog.models import Product

# VAG zīmolu nosaukumu fragmenti
VAG_PATTERNS = ['audi', 'volkswagen', 'vw ', 'skoda', 'seat', 'cupra']

# Produktu ID
PROD_504_507 = [57, 58]   # 5W-30 504/507
PROD_502     = []          # 5W-40 502.00 (ja nav - tukšs)

YEAR_RE = re.compile(r'\((\d{4})\s*[-–]\s*\d{4}')


def extract_year(name):
    m = YEAR_RE.search(name)
    return int(m.group(1)) if m else None


def run():
    # Pārbauda vai produkti eksistē
    prods_504 = list(Product.objects.filter(id__in=PROD_504_507, is_active=True))
    if not prods_504:
        print('! 504/507 produkti nav atrasti, beidzu')
        return
    print(f'Produkti 504/507: {[p.name_lv for p in prods_504]}')

    # Atrod VAG zīmolus
    all_brands = CarBrand.objects.filter(is_active=True)
    vag_brands = [b for b in all_brands if any(p in b.name.lower() for p in VAG_PATTERNS)]
    print(f'VAG zīmoli: {len(vag_brands)}')
    for b in vag_brands:
        print(f'  {b.name} (id={b.id})')

    existing_mod_ids = set(ProductCompatibility.objects.values_list('modification_id', flat=True))

    new_compat = 0
    skipped_old = 0
    skipped_has_compat = 0

    for brand in vag_brands:
        mods = CarModification.objects.filter(
            car_model__brand=brand, is_active=True
        ).select_related('car_model')

        for mod in mods:
            if mod.id in existing_mod_ids:
                skipped_has_compat += 1
                continue

            year = extract_year(mod.name)

            if year is None or year >= 2004:
                target_prods = prods_504
            else:
                skipped_old += 1
                continue  # Vecākām nav pietiekamas datu bāzes

            for prod in target_prods:
                _, created = ProductCompatibility.objects.get_or_create(
                    product=prod,
                    modification=mod,
                    defaults={'note_lv': '', 'note_ru': '', 'note_en': '', 'note_de': ''}
                )
                if created:
                    new_compat += 1

    total = ProductCompatibility.objects.count()
    print(f'\n=== Rezultāts ===')
    print(f'  Jauni compat ieraksti:   {new_compat}')
    print(f'  Izlaistas (jau ir compat): {skipped_has_compat}')
    print(f'  Izlaistas (pirms 2004):   {skipped_old}')
    print(f'  Kopā compat:             {total}')


if __name__ == '__main__':
    run()
