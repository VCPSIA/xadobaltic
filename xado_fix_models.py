"""
Imports models for brands that have 0 models.
Run: venv\Scripts\python.exe xado_fix_models.py
"""
import os, sys, re, time
import django
import requests, urllib3
from bs4 import BeautifulSoup
from django.utils.text import slugify

urllib3.disable_warnings()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility
from catalog.models import VehicleType, Product

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer': 'https://xado.ua/ua/',
}
session = requests.Session()
session.headers.update(HEADERS)
session.verify = False
DELAY = 0.4

def post_api(route, data):
    url = f'https://xado.ua/index.php?route=information/oil_selection/{route}'
    for attempt in range(3):
        try:
            r = session.post(url, data=data, timeout=20)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            if attempt == 2:
                print(f'  ! {route}: {e}')
            time.sleep(1)
    return None

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
    if any(k in nl for k in ['tdi','cdi','tdci','cdti','dci','hdi','crdi','jtdm']):
        fuel = 'diesel'
    elif any(k in nl for k in ['tfsi','tsi','gdi','mpi','fsi','vtec','vvti']):
        fuel = 'gasoline'
    elif 'electric' in nl:
        fuel = 'electric'
    elif 'hybrid' in nl:
        fuel = 'hybrid'
    yf, yt = parse_year_range(name)
    power = None
    pm = re.search(r'\b(\d{2,4})\s*(?:hp|к\.с|л\.с)\b', name, re.I)
    if pm:
        power = int(pm.group(1))
    return engine, fuel, power, yf, yt

def _extract_keywords(name):
    name_up = name.upper()
    visc = re.search(r'\b(\d{1,2}W[-–]\d{1,2})\b', name_up)
    visc = visc.group(1).replace('–', '-') if visc else ''
    specs = re.findall(r'\b(?:C\d+|GL[-–]?\d+|ATF(?:\s*(?:III|IV|V|VI)\+?)|\d{3}/\d{3}|SN|CF[-\d]*|SM|CJ[-\d]*|CI[-\d]*|SL|SG|DEXOS\d*)\b', name_up)
    return visc, set(specs)

_local_products = None

def get_local_products():
    global _local_products
    if _local_products is None:
        _local_products = list(Product.objects.filter(is_active=True).only('id', 'name_lv', 'viscosity', 'sku'))
    return _local_products

def match_products(ua_name):
    ua_visc, ua_specs = _extract_keywords(ua_name)
    if not ua_visc:
        return []
    results = []
    for p in get_local_products():
        lv = p.name_lv.upper()
        if ua_visc not in lv:
            continue
        _, lv_specs = _extract_keywords(lv)
        common = ua_specs & lv_specs
        score = len(common)
        if score > 0 or (not ua_specs and not lv_specs):
            results.append((score, p))
    results.sort(key=lambda x: -x[0])
    if not results:
        return []
    best = results[0][0]
    return [p for s, p in results if s == best]

def get_engine_products(resp):
    import json
    html_val = resp.get('html') or {}
    if isinstance(html_val, str):
        try:
            html_val = json.loads(html_val)
        except Exception:
            return []
    if not isinstance(html_val, dict):
        return []
    result_arr = html_val.get('result_arr', {})
    out = []
    OIL_COMPONENTS = {1, 3, 4, 7}
    for sys_name, sys_data in result_arr.items():
        if sys_data.get('component_id', 0) not in OIL_COMPONENTS:
            continue
        for _, prod_dict in sys_data.get('products', {}).items():
            if not isinstance(prod_dict, dict):
                continue
            for xado_id, prod_info in prod_dict.items():
                if not isinstance(prod_info, dict):
                    continue
                name = re.sub(r'^Motor\s+oil\s+', '', prod_info.get('name', ''), flags=re.I).strip()
                name = re.sub(r'[а-яА-ЯіїєёЁ]+.*$', '', name).strip()
                if name:
                    out.append(name)
    return out

# ─── Galvenais ─────────────────────────────────────────────────────────────────

# Iegūst xado.ua brand ID → name kartēšanu
vt_id = 1
resp = post_api('getBrands', {'vehicle_type_id': vt_id})
xado_brands = {t: v for v, t in parse_options(resp.get('html', '')) if v != '0'}
print(f'xado.ua: {len(xado_brands)} markas')

# Atrod lokālās markas bez modeļiem
empty_brands = CarBrand.objects.annotate_models = None
from django.db.models import Count
empty_brands = CarBrand.objects.annotate(mc=Count('models')).filter(mc=0)
print(f'Lokāli bez modeļiem: {empty_brands.count()}')

stats = {'models': 0, 'mods': 0, 'compat': 0}

vt = VehicleType.objects.filter(name_en='Passenger cars').first()
if not vt:
    vt = VehicleType.objects.first()

for brand in empty_brands:
    # Meklē xado.ua ID pēc nosaukuma
    xado_id = None
    for xname, xid in xado_brands.items():
        if xname == brand.name:
            xado_id = xid
            break
    if not xado_id:
        continue

    time.sleep(DELAY)
    mresp = post_api('getModels', {'vehicle_type_id': vt_id, 'vehicle_type_make_id': xado_id})
    if not mresp:
        continue
    models_raw = [(v, t) for v, t in parse_options(mresp.get('html', '')) if v != '0']
    if not models_raw:
        continue

    for model_ua_id, model_raw in models_raw:
        clean = clean_model_name(model_raw)
        yf, yt = parse_year_range(model_raw)
        model, m_cr = CarModel.objects.get_or_create(
            brand=brand, name=clean,
            defaults={'vehicle_type': vt, 'year_from': yf, 'year_to': yt, 'is_active': True}
        )
        if m_cr:
            stats['models'] += 1

        time.sleep(DELAY)
        tresp = post_api('getTypes', {
            'vehicle_type_id': vt_id,
            'vehicle_type_make_id': xado_id,
            'vehicle_type_make_model_id': model_ua_id,
        })
        if not tresp:
            continue
        mods_raw = [(v, t) for v, t in parse_options(tresp.get('html', '')) if v != '0']

        for mod_ua_id, mod_name in mods_raw:
            engine, fuel, power, yf2, yt2 = parse_mod_attrs(mod_name)
            mod, mod_cr = CarModification.objects.get_or_create(
                car_model=model, name=mod_name,
                defaults={'engine_volume': engine, 'fuel_type': fuel,
                          'power_hp': power, 'year_from': yf2, 'year_to': yt2, 'is_active': True}
            )
            if mod_cr:
                stats['mods'] += 1

            time.sleep(DELAY)
            presp = post_api('getProducts', {
                'vehicle_type_id': vt_id,
                'vehicle_type_make_id': xado_id,
                'vehicle_type_make_model_id': model_ua_id,
                'vehicle_type_make_model_type_id': mod_ua_id,
            })
            if not presp:
                continue
            for ua_name in get_engine_products(presp):
                for lp in match_products(ua_name):
                    _, cc = ProductCompatibility.objects.get_or_create(
                        product=lp, modification=mod,
                        defaults={'note_lv': '', 'note_ru': '', 'note_en': '', 'note_de': ''}
                    )
                    if cc:
                        stats['compat'] += 1

    print(f'  {brand.name}: {len(models_raw)} modeļi importēti')

print(f'\nGatavs: +{stats["models"]} modeļi, +{stats["mods"]} mods, +{stats["compat"]} saderības')
