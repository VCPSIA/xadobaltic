"""
Ielādē OEM specifikācijas no Liqui-Moly produktu lapām un saglabā CarModification.oil_spec.
Darbība:
  1. Katrai modifikācijai iegūst LM rekomendāciju
  2. Paņem primāro produktu
  3. No produktu keša (vai tīkla) iegūst OEM apstiprinājumus
  4. Saglabā oil_viscosity + oil_spec

Palaišana: venv/Scripts/python.exe fill_oil_specs.py [--brand BMW] [--limit 5]
"""
import os, sys, re, time, argparse, requests, urllib3, django

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, r'C:\Users\USER\xadobaltic')
django.setup()

from django.db import connection
from selector.models import CarBrand, CarModel, CarModification

# Iespēj WAL režīmu labākai paralēlismam
with connection.cursor() as cur:
    cur.execute('PRAGMA journal_mode=WAL;')
    cur.execute('PRAGMA busy_timeout=30000;')

OAPI = 'https://openapi.liqui-moly.com'
LM = 'https://www.liqui-moly.com'
AUTH = 'Basic bGltbzpsaW1v'
CLIENT = '10'
COUNTRY = 'DEU'
LANG = 'DEU'
BASE = f'/api/v2/oww/{CLIENT}/{COUNTRY}/{LANG}'

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Authorization': AUTH,
})

# Keš: {prod_id: "ACEA C3, BMW LL-04, ..."}
PROD_SPEC_CACHE = {}


def api_get(path, retries=2):
    for _ in range(retries):
        try:
            r = SESSION.get(f'{OAPI}{path}', timeout=15, verify=False)
            if r.status_code == 200:
                return r.json()
        except:
            time.sleep(1)
    return None


def normalize_spec(raw):
    """Normalizē OEM specifikāciju tekstu."""
    s = raw.strip()
    # Apvienojam VW 504 00 -> VW 504.00
    s = re.sub(r'VW (\d{3}) (\d{2})', r'VW \1.\2', s)
    # MB-Freigabe 229.51 -> MB 229.51
    s = re.sub(r'MB-Freigabe\s+', 'MB ', s)
    # BMW Longlife-04 -> BMW LL-04
    s = re.sub(r'BMW Longlife-?(\d+)', r'BMW LL-\1', s)
    # BMW Longlife-01 FE -> BMW LL-01 FE
    s = re.sub(r'BMW LL-(\d+)\s+FE', r'BMW LL-\1FE', s)
    # Apvienojam dublikātus
    parts = [p.strip() for p in re.split(r'[,;/]', s) if p.strip()]
    # Unikāli, saglabājam kārtību
    seen = set()
    unique = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return ', '.join(unique)


def get_product_specs(prod_id):
    """Ielādē LM produkta lapu un izvelk OEM specifikācijas."""
    if prod_id in PROD_SPEC_CACHE:
        return PROD_SPEC_CACHE[prod_id]

    r = SESSION.get(f'{LM}/de/de/tinyurl/{prod_id}',
                    timeout=15, verify=False, allow_redirects=True)
    if r.status_code != 200:
        PROD_SPEC_CACHE[prod_id] = ''
        return ''

    html = r.text
    time.sleep(0.5)

    # Metode 1: JSON lauki ar apstiprinājumiem
    json_specs = re.findall(r'"(?:approvals|freigaben|specifications)"\s*:\s*"([^"]{10,500})"', html, re.I)
    if json_specs:
        best = max(json_specs, key=len)
        result = normalize_spec(best)
        PROD_SPEC_CACHE[prod_id] = result
        return result

    # Metode 2: Meklē struktūrētus spec kodus (nevis brīvu tekstu)
    # Katrs spec kods atdalīts ar komatu/semikolu/atstarpi
    SPEC_TOKEN = r'(?:ACEA\s+[A-E]\d[\w./]*|API\s+[A-Z]{2,4}[\w./]*|BMW\s+LL[-\s]?\d+[\w.\s]*|BMW\s+Longlife[-\s]?\d+[\w.\s]*|VW\s+\d{3}[\w./]*|MB[-\s]\d+\.\d+[\w./]*|MB-Freigabe\s+\d+\.\d+[\w./]*|Porsche\s+[A-Z]\d+[\w./]*|JASO\s+[A-Z]+\d*|GM\s+LL-\w+|Ford\s+WSS-\w+|Renault\s+RN[-\s]\w+|PSA\s+B71\s*\w*|Fiat\s+[\d.]+|Peugeot\s+B71\s*\w*)'
    tokens_found = re.findall(SPEC_TOKEN, html)
    # Filtrē duplikātus saglabājot kārtību
    seen_t = set()
    unique_tokens = []
    for t in tokens_found:
        t_clean = t.strip().rstrip('.,;')
        key = t_clean.lower()
        if key not in seen_t and len(t_clean) >= 4:
            seen_t.add(key)
            unique_tokens.append(t_clean)

    if not unique_tokens:
        PROD_SPEC_CACHE[prod_id] = ''
        return ''

    raw = ', '.join(unique_tokens[:20])  # max 20 tokeni
    normalized = normalize_spec(raw)
    PROD_SPEC_CACHE[prod_id] = normalized
    return normalized


def extract_from_rec(rec_json):
    """No LM rekomendāciju JSON izvelk viskozitāti un produkta ID specifikācijām."""
    if not rec_json:
        return '', '', ''

    motor = rec_json.get('results', {}).get('Motor', {})
    uses = motor.get('uses', {})
    if not uses:
        return '', '', ''

    # Prioritāte: "Vorzugsweise" > "Normal" > jebkurš pirmais
    priority_order = ['vorzugsweise', 'flexibel (max)', 'normal']
    primary_use = None
    for key in uses:
        for prio in priority_order:
            if prio in key.lower():
                primary_use = uses[key]
                break
        if primary_use:
            break
    if not primary_use:
        primary_use = list(uses.values())[0]

    products = primary_use.get('products', {})
    if not products:
        return '', '', ''

    # Pirmais produkts = galvenā rekomendācija
    first_prod_id = list(products.keys())[0]
    first_prod_name = products[first_prod_id]['name']

    # Viskozitāte no visiem primārā use produktiem
    viscs = set()
    for prod in products.values():
        name = prod.get('name', '')
        for v in re.findall(r'\b\d+W[-–]\d+\b', name, re.I):
            viscs.add(v.upper())

    if viscs:
        sorted_v = sorted(viscs, key=lambda x: (int(x.split('W')[0]), int(x.split('-')[1])))
        visc_str = ', '.join(sorted_v)
    else:
        visc_str = ''

    return visc_str, first_prod_id, first_prod_name


def fill_specs(brand_filter=None, limit=None, overwrite=False):
    mods = CarModification.objects.filter(lm_id__gt='').select_related(
        'car_model__brand'
    )
    if not overwrite:
        mods = mods.filter(oil_spec='')
    if brand_filter:
        mods = mods.filter(car_model__brand__name__icontains=brand_filter)
    if limit:
        mods = mods[:limit]

    total = mods.count()
    print(f"Apstrādā {total} modifikācijas...")

    updated = 0
    for i, mod in enumerate(mods.iterator(chunk_size=100), 1):
        brand = mod.car_model.brand.name
        model = mod.car_model.name
        name = mod.name
        lm_path = mod.lm_id

        # Atjekonstruē LM API ceļu no lm_id hierarhijas
        # lm_id ir pēdējais ceļa segments; vajag arī brand_lm_id un model_lm_id
        brand_obj = mod.car_model.brand
        model_obj = mod.car_model

        # Iegūst LM IDs no saistītajiem objektiem
        brand_lm = brand_obj.lm_id
        model_lm = model_obj.lm_id
        cat = model_obj.lm_category or 1

        if not brand_lm or not model_lm:
            continue

        rec_path = f'{BASE}/{cat}/{brand_lm}/{model_lm}/{lm_path}/'
        rec = api_get(rec_path)

        visc, prod_id, prod_name = extract_from_rec(rec)

        spec = ''
        if prod_id:
            spec = get_product_specs(prod_id)

        if visc or spec:
            update_fields = []
            if visc and not mod.oil_viscosity:
                mod.oil_viscosity = visc
                update_fields.append('oil_viscosity')
            if spec and (not mod.oil_spec or overwrite):
                mod.oil_spec = spec
                update_fields.append('oil_spec')
            if update_fields:
                for attempt in range(5):
                    try:
                        mod.save(update_fields=update_fields)
                        updated += 1
                        break
                    except Exception:
                        time.sleep(2 ** attempt)
                else:
                    print(f'  KĻŪDA: nevar saglabāt mod {mod.pk}')

        if i % 10 == 0 or i <= 5:
            print(f"  [{i}/{total}] {brand} / {name}: visc={visc}, spec={spec[:60] if spec else '-'}")

        time.sleep(0.4)

    print(f"\nPabeigts! Atjaunots: {updated}/{total}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--brand', type=str, default=None)
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    fill_specs(brand_filter=args.brand, limit=args.limit, overwrite=args.overwrite)
