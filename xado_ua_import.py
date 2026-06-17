"""
Imports car oil compatibility data from xado.ua.
Run: venv\Scripts\python.exe xado_ua_import.py

  vehicle_type_id values from xado.ua:
    1=Vieglais auto, 2=Vieglie kravas, 3=Smagais kravas, 4=Motocikls, 5=Lauksaimn.

  Flow: getBrands -> getModels -> getTypes -> getProducts
  getProducts returns JSON with 'html' key which is itself a JSON string
  containing 'result_arr' (structured product data per system type).
"""

import os, sys, re, time, json
import django
import requests
import urllib3
from bs4 import BeautifulSoup
from django.utils.text import slugify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility
from catalog.models import VehicleType, Product

# ─── CONFIG ────────────────────────────────────────────────────────────────────
BASE   = 'https://xado.ua'
DELAY  = 0.4    # seconds between requests

# Set to small numbers for testing, 9999 for full import
MAX_BRANDS = 9999
MAX_MODELS = 9999
MAX_MODS   = 9999

VEHICLE_TYPES_UA = {
    1: ('Vieglais auto',        'Легковые',            'Passenger cars',    'PKW'),
    2: ('Vieglie kravas',       'Лёгкие грузовые',     'Light commercial',  'Leichte LKW'),
    3: ('Smagais kravas/Autob.','Тяжёлые грузовые',    'Heavy truck/Bus',   'Schwere LKW'),
    4: ('Motocikls',            'Мотоцикл',            'Motorcycle',        'Motorrad'),
    5: ('Lauksaimn. tehnika',   'Сельхозтехника',      'Agricultural',      'Landmaschinen'),
}

HEADERS = {
    'User-Agent':      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'X-Requested-With':'XMLHttpRequest',
    'Content-Type':    'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer':         'https://xado.ua/ua/',
    'Accept':          'application/json, text/javascript, */*; q=0.01',
}

session = requests.Session()
session.headers.update(HEADERS)
session.verify = False

# ─── HTTP ──────────────────────────────────────────────────────────────────────

def post_api(route, data, retries=3):
    url = f'{BASE}/index.php?route=information/oil_selection/{route}'
    for attempt in range(retries):
        try:
            r = session.post(url, data=data, timeout=20)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            if attempt == retries - 1:
                print(f'  ! {route} error: {e}')
            time.sleep(1)
    return None

# ─── PARSĒŠANA ─────────────────────────────────────────────────────────────────

def parse_options(html):
    soup = BeautifulSoup(html or '', 'html.parser')
    return [(o['value'], o.get_text(strip=True))
            for o in soup.find_all('option') if o.get('value')]

def clean_model_name(text):
    return re.sub(r'\s*\(\d{4}[\s\-–]+[\d\w\.]+\)\s*$', '', text).strip()

def parse_year_range(text):
    m = re.search(r'\((\d{4})\s*[-–]\s*(\d{4}|н\.в\.|present|сьогодні)\)', text)
    if not m:
        return None, None
    return int(m.group(1)), (int(m.group(2)) if m.group(2).isdigit() else None)

def parse_mod_attrs(name):
    engine = ''
    m = re.search(r'\b(\d+\.\d+)\b', name)
    if m:
        engine = m.group(1)
    nl = name.lower()
    fuel = ''
    if any(k in nl for k in ['tdi','cdi','tdci','cdti','dci','hdi','crdi','jtdm','tdv','d4d','d5244']):
        fuel = 'diesel'
    elif any(k in nl for k in ['tfsi','tsi','gdi','mpi','fsi','vtec','vvti','gti','vvt']):
        fuel = 'gasoline'
    elif 'electric' in nl or 'електр' in nl:
        fuel = 'electric'
    elif 'hybrid' in nl or 'гібрид' in nl:
        fuel = 'hybrid'
    elif 'lpg' in nl or ' газ' in nl:
        fuel = 'lpg'
    power = None
    for pat in [r'\b(\d{2,4})\s*(?:hp|к\.с|л\.с)\b']:
        pm = re.search(pat, name, re.I)
        if pm:
            power = int(pm.group(1))
            break
    yf, yt = parse_year_range(name)
    return engine, fuel, power, yf, yt

# ─── PRODUKTU SASKAŅOŠANA ──────────────────────────────────────────────────────

def _extract_keywords(name):
    """Extracts viscosity grade and spec keywords from a product name."""
    name_up = name.upper()
    visc = re.search(r'\b(\d{1,2}W[-–]\d{1,2})\b', name_up)
    visc = visc.group(1).replace('–', '-') if visc else ''
    # Spec tokens: C3, C23, C4, 504/507, SN, CF, GL-4, ATF only
    specs = re.findall(r'\b(?:C\d+|GL[-–]?\d+|ATF(?:\s*(?:III|IV|V|VI)\+?)|\d{3}/\d{3}|SN|CF[-\d]*|SM|CJ[-\d]*|CI[-\d]*|SL|SG|DEXOS\d*|A3B4|A5B5|505\.\d+)\b', name_up)
    return visc, set(specs)

_local_products = None

def get_local_products():
    global _local_products
    if _local_products is None:
        _local_products = list(Product.objects.filter(is_active=True).only('id', 'name_lv', 'viscosity', 'sku'))
    return _local_products

def match_products(ua_name):
    """Returns list of local Product objects that best match the xado.ua product name."""
    ua_visc, ua_specs = _extract_keywords(ua_name)
    if not ua_visc:
        return []

    results = []
    for p in get_local_products():
        lv = p.name_lv.upper()
        # Viscosity must match
        if ua_visc not in lv:
            continue
        # Check how many spec tokens match
        lv_visc2, lv_specs = _extract_keywords(lv)
        common = ua_specs & lv_specs
        score = len(common)
        # Require at least one spec token in common, or very similar name
        if score > 0 or (ua_specs and not lv_specs):
            results.append((score, p))

    # Return top matches by score
    results.sort(key=lambda x: -x[0])
    # Only return if best score >= 1 or only 1 candidate
    if not results:
        return []
    best_score = results[0][0]
    if best_score == 0:
        # No spec match — return all with matching viscosity only if ≤3 products
        return [p for _, p in results[:3]]
    return [p for score, p in results if score == best_score]

def get_engine_products_from_response(resp):
    """
    resp: API response dict with 'html' key (which is a JSON string).
    Returns list of (ua_product_name, note) for engine/oil type products.
    """
    html_val = resp.get('html', {})
    if not html_val:
        return []
    # 'html' can be a dict or a JSON string
    if isinstance(html_val, str):
        try:
            html_val = json.loads(html_val)
        except (json.JSONDecodeError, TypeError):
            return []
    result_arr = html_val.get('result_arr', {})
    if not result_arr:
        return []

    products_out = []
    # Engine oils: component_id = 1 (Engine), also include gearbox/atf oils
    OIL_COMPONENTS = {1, 3, 4, 7}  # Engine, Transmission auto, Transmission manual, Differential
    for system_name, system_data in result_arr.items():
        comp_id = system_data.get('component_id', 0)
        if comp_id not in OIL_COMPONENTS:
            continue
        for prod_key, prod_dict in system_data.get('products', {}).items():
            if not isinstance(prod_dict, dict):
                continue
            for xado_id, prod_info in prod_dict.items():
                if not isinstance(prod_info, dict):
                    continue
                name = prod_info.get('name', '').strip()
                # Remove "Motor oil" prefix
                name = re.sub(r'^Motor\s+oil\s+', '', name, flags=re.I).strip()
                # Remove Ukrainian text (Cyrillic suffix)
                name = re.sub(r'[а-яА-ЯіїєёЁ]+.*$', '', name).strip()
                if name:
                    products_out.append((name, system_name))
    return products_out

# ─── SLUG ─────────────────────────────────────────────────────────────────────

_used_slugs = None

def make_slug(name):
    global _used_slugs
    if _used_slugs is None:
        _used_slugs = set(CarBrand.objects.values_list('slug', flat=True))
    base = slugify(name) or re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'brand'
    slug, n = base, 1
    while slug in _used_slugs:
        slug = f'{base}-{n}'; n += 1
    _used_slugs.add(slug)
    return slug

# ─── VEHICLE TYPES ─────────────────────────────────────────────────────────────

def ensure_vehicle_types():
    vt_map = {}
    for ua_id, (lv, ru, en, de) in VEHICLE_TYPES_UA.items():
        vt, created = VehicleType.objects.get_or_create(
            name_en=en,
            defaults={'name_lv': lv, 'name_ru': ru, 'name_de': de,
                      'slug': slugify(en), 'order': ua_id}
        )
        if created:
            print(f'  + VehicleType: {lv}')
        vt_map[ua_id] = vt
    return vt_map

# ─── GALVENĀ IMPORTA FUNKCIJA ──────────────────────────────────────────────────

def run():
    print('=== XADO UA Import sākts ===\n')
    stats = {'brands': 0, 'models': 0, 'mods': 0, 'compat': 0, 'skipped': 0}

    vt_map = ensure_vehicle_types()

    for ua_vt_id, vt in vt_map.items():
        print(f'\n── {vt.name_lv} (xado id={ua_vt_id}) ──')

        resp = post_api('getBrands', {'vehicle_type_id': ua_vt_id})
        if not resp:
            continue
        brands_raw = [(v, t) for v, t in parse_options(resp.get('html', '')) if v != '0']
        print(f'  Markas: {len(brands_raw)}')

        for bi, (brand_ua_id, brand_name) in enumerate(brands_raw[:MAX_BRANDS]):
            brand, created = CarBrand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': make_slug(brand_name), 'is_active': True}
            )
            if created:
                stats['brands'] += 1
            if not brand.vehicle_types.filter(id=vt.id).exists():
                brand.vehicle_types.add(vt)

            time.sleep(DELAY)
            mresp = post_api('getModels', {'vehicle_type_id': ua_vt_id, 'vehicle_type_make_id': brand_ua_id})
            if not mresp:
                continue
            models_raw = [(v, t) for v, t in parse_options(mresp.get('html', '')) if v != '0']
            if not models_raw:
                continue

            for mi, (model_ua_id, model_raw) in enumerate(models_raw[:MAX_MODELS]):
                clean_name = clean_model_name(model_raw)
                yf, yt = parse_year_range(model_raw)
                model, m_created = CarModel.objects.get_or_create(
                    brand=brand, name=clean_name,
                    defaults={'vehicle_type': vt, 'year_from': yf, 'year_to': yt, 'is_active': True}
                )
                if m_created:
                    stats['models'] += 1

                time.sleep(DELAY)
                tresp = post_api('getTypes', {
                    'vehicle_type_id': ua_vt_id,
                    'vehicle_type_make_id': brand_ua_id,
                    'vehicle_type_make_model_id': model_ua_id,
                })
                if not tresp:
                    continue
                mods_raw = [(v, t) for v, t in parse_options(tresp.get('html', '')) if v != '0']
                if not mods_raw:
                    continue

                for ti, (mod_ua_id, mod_name) in enumerate(mods_raw[:MAX_MODS]):
                    engine, fuel, power, yf2, yt2 = parse_mod_attrs(mod_name)
                    mod, mod_created = CarModification.objects.get_or_create(
                        car_model=model, name=mod_name,
                        defaults={
                            'engine_volume': engine, 'fuel_type': fuel,
                            'power_hp': power, 'year_from': yf2, 'year_to': yt2,
                            'is_active': True,
                        }
                    )
                    if mod_created:
                        stats['mods'] += 1

                    time.sleep(DELAY)
                    presp = post_api('getProducts', {
                        'vehicle_type_id': ua_vt_id,
                        'vehicle_type_make_id': brand_ua_id,
                        'vehicle_type_make_model_id': model_ua_id,
                        'vehicle_type_make_model_type_id': mod_ua_id,
                    })
                    if not presp:
                        continue

                    ua_products = get_engine_products_from_response(presp)
                    for ua_name, system_name in ua_products:
                        local_prods = match_products(ua_name)
                        if not local_prods:
                            stats['skipped'] += 1
                            continue
                        for lp in local_prods:
                            _, c_created = ProductCompatibility.objects.get_or_create(
                                product=lp, modification=mod,
                                defaults={'note_lv': '', 'note_ru': '', 'note_en': '', 'note_de': ''}
                            )
                            if c_created:
                                stats['compat'] += 1

            pct = int((bi + 1) / max(len(brands_raw), 1) * 100)
            print(f'  [{pct:3d}%] {brand_name}: {len(models_raw)} modeļi, '
                  f'{stats["mods"]} mods kopā, {stats["compat"]} saderības')

    # Cleanup
    import os
    for f in ['test_brands.html', 'test_products.html', 'products_list.txt']:
        try:
            os.remove(f)
        except Exception:
            pass

    print(f'\n=== Importēts ===')
    print(f'  Jaunas markas:        {stats["brands"]}')
    print(f'  Jauni modeļi:         {stats["models"]}')
    print(f'  Jaunas modifikācijas: {stats["mods"]}')
    print(f'  Saderības ieraksti:   {stats["compat"]}')
    print(f'  Nesaskaņoti produkti: {stats["skipped"]}')


if __name__ == '__main__':
    run()

