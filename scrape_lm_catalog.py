"""
Liqui-Moly OWW API → XADO DB
Ielādē auto katalogu un motoreļļas viskozitāti.
Palaišana: venv\Scripts\python.exe scrape_lm_catalog.py [--cat 1] [--brand BMW] [--limit 5]
"""
import os, sys, re, time, json, argparse, requests, urllib3, django

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, r'C:\Users\USER\xadobaltic')
django.setup()

from selector.models import CarBrand, CarModel, CarModification
from django.utils.text import slugify

# Liqui-Moly OWW API
OAPI = 'https://openapi.liqui-moly.com'
AUTH = 'Basic bGltbzpsaW1v'
CLIENT = '10'
COUNTRY = 'DEU'
LANG = 'DEU'
BASE = f'/api/v2/oww/{CLIENT}/{COUNTRY}/{LANG}'

LM_CATEGORIES = {
    1: 'Pkw',
    2: 'Van',
    3: 'LKW',
    4: 'Moto',
}

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json',
    'Authorization': AUTH,
})

def api_get(path, retries=3):
    for attempt in range(retries):
        try:
            r = SESSION.get(f'{OAPI}{path}', timeout=20, verify=False)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                print(f"  Rate limit, gaidu 5s...")
                time.sleep(5)
            else:
                print(f"  HTTP {r.status_code} → {path}")
                return None
        except Exception as e:
            print(f"  ERR: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    return None

def extract_viscosity(rec_json):
    """Izvelk motoreļļas viskozitāti no LM rekomendāciju JSON."""
    if not rec_json:
        return ''
    motor = rec_json.get('results', {}).get('Motor', {})
    viscs = set()
    for use_data in motor.get('uses', {}).values():
        for prod in use_data.get('products', {}).values():
            name = prod.get('name', '')
            matches = re.findall(r'\b\d+W[-–]\d+\b', name, re.I)
            viscs.update(m.upper() for m in matches)
    if viscs:
        sorted_v = sorted(viscs, key=lambda x: (int(x.split('W')[0]), int(x.split('-')[1])))
        return ', '.join(sorted_v)
    return ''

def make_slug(name, existing_slugs):
    base = slugify(name)[:45]
    slug = base
    i = 2
    while slug in existing_slugs:
        slug = f"{base}-{i}"
        i += 1
    existing_slugs.add(slug)
    return slug

def scrape(categories=None, brand_filter=None, limit_brands=None, skip_recs=False):
    cats = categories or list(LM_CATEGORIES.keys())
    existing_slugs = set(CarBrand.objects.values_list('slug', flat=True))

    for cat_id in cats:
        cat_name = LM_CATEGORIES.get(cat_id, str(cat_id))
        print(f"\n{'='*60}")
        print(f"KATEGORIJA: {cat_name} (id={cat_id})")

        brands_data = api_get(f'{BASE}/{cat_id}/')
        if not brands_data:
            continue
        makes = brands_data.get('makes', [])
        print(f"  {len(makes)} markas")

        if brand_filter:
            makes = [m for m in makes if brand_filter.upper() in m['name'].upper()]
            print(f"  Filtrs '{brand_filter}': {len(makes)} markas")

        if limit_brands:
            makes = makes[:limit_brands]

        for brand_data in makes:
            bname = brand_data['name']
            blm_id = brand_data['id']

            # Izveido vai atrod CarBrand
            brand_obj, created = CarBrand.objects.get_or_create(
                lm_id=blm_id,
                defaults={
                    'name': bname,
                    'slug': make_slug(bname, existing_slugs),
                    'is_active': True,
                }
            )
            if created:
                print(f"\n  + MARKA: {bname}")
            else:
                print(f"\n  ~ MARKA: {bname} (jau eksistē)")

            # Modeļi
            models_data = api_get(f'{BASE}/{cat_id}/{blm_id}/')
            if not models_data:
                continue
            model_list = models_data.get('models', [])
            print(f"    {len(model_list)} modeļi")
            time.sleep(0.3)

            for model_data in model_list:
                mname = model_data['name']
                mlm_id = model_data['id']

                # Parsa gadus no nosaukuma, piemēram "1er-Serie, E81 (2004-2013)"
                year_match = re.search(r'\((\d{4})-?(\d{4})?', mname)
                year_from = int(year_match.group(1)) if year_match else None
                year_to_str = year_match.group(2) if year_match else None
                year_to = int(year_to_str) if year_to_str else None

                model_obj, mcreated = CarModel.objects.get_or_create(
                    lm_id=mlm_id,
                    defaults={
                        'brand': brand_obj,
                        'name': mname,
                        'lm_category': cat_id,
                        'year_from': year_from,
                        'year_to': year_to,
                        'is_active': True,
                    }
                )
                if mcreated:
                    print(f"      + Modelis: {mname}")

                # Modifikācijas
                types_data = api_get(f'{BASE}/{cat_id}/{blm_id}/{mlm_id}/')
                if not types_data:
                    continue
                type_list = types_data.get('types', [])
                time.sleep(0.3)

                for type_data in type_list:
                    tname = type_data['name']
                    tlm_id = type_data['id']
                    tlink = type_data.get('link', '')

                    mod_obj, tcreated = CarModification.objects.get_or_create(
                        lm_id=tlm_id,
                        defaults={
                            'car_model': model_obj,
                            'name': tname,
                            'is_active': True,
                        }
                    )

                    # Iegūst viskozitāti (ja vēl nav un nav skip_recs)
                    if not skip_recs and not mod_obj.oil_viscosity:
                        rec = api_get(tlink)
                        visc = extract_viscosity(rec)
                        if visc:
                            mod_obj.oil_viscosity = visc
                            mod_obj.save(update_fields=['oil_viscosity'])
                        time.sleep(0.5)

                    status = '+' if tcreated else '~'
                    visc_info = f" [{mod_obj.oil_viscosity}]" if mod_obj.oil_viscosity else ''
                    print(f"        {status} {tname}{visc_info}")

    total_brands = CarBrand.objects.count()
    total_models = CarModel.objects.count()
    total_mods = CarModification.objects.count()
    print(f"\n{'='*60}")
    print(f"PABEIGTS! DB: {total_brands} markas, {total_models} modeļi, {total_mods} modifikācijas")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cat', type=int, nargs='+', default=None, help='LM kategorijas (1=Pkw, 2=Van, 3=LKW, 4=Moto)')
    parser.add_argument('--brand', type=str, default=None, help='Filtrē pēc markas nosaukuma')
    parser.add_argument('--limit', type=int, default=None, help='Maks. marku skaits')
    parser.add_argument('--skip-recs', action='store_true', help='Neielādē rekomendācijas (tikai katalogs)')
    args = parser.parse_args()

    scrape(
        categories=args.cat,
        brand_filter=args.brand,
        limit_brands=args.limit,
        skip_recs=args.skip_recs,
    )
