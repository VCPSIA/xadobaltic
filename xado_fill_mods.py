"""
Aizpilda trūkstošās modifikācijas modeļiem, kuriem ir 0 modifikāciju.
Traversē xado.ua API: getBrands → getModels → getTypes → getProducts
"""
import os, sys, re, time, json
import django
import requests
import urllib3
from bs4 import BeautifulSoup
from django.utils.text import slugify

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility
from catalog.models import VehicleType, Product

BASE  = 'https://xado.ua'
DELAY = 0.5

VEHICLE_TYPES_UA = {1: 'Passenger cars', 2: 'Light commercial',
                    3: 'Heavy truck/Bus', 4: 'Motorcycle', 5: 'Agricultural'}

HEADERS = {
    'User-Agent':       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type':     'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer':          'https://xado.ua/ua/',
    'Accept':           'application/json, text/javascript, */*; q=0.01',
}

session = requests.Session()
session.headers.update(HEADERS)
session.verify = False


def post_api(route, data, retries=4):
    url = f'{BASE}/index.php?route=information/oil_selection/{route}'
    for attempt in range(retries):
        try:
            r = session.post(url, data=data, timeout=25)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            if attempt == retries - 1:
                print(f'  ! {route} kludaa: {e}')
            time.sleep(2 ** attempt)
    return None


def parse_options(html):
    soup = BeautifulSoup(html or '', 'html.parser')
    return [(o['value'], o.get_text(strip=True))
            for o in soup.find_all('option') if o.get('value')]


def clean_model_name(text):
    return re.sub(r'\s*\(\d{4}[\s\-]+[\d\w\.]+\)\s*$', '', text).strip()


def parse_year_range(text):
    m = re.search(r'\((\d{4})\s*[-]\s*(\d{4}|present)\)', text)
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
    if any(k in nl for k in ['tdi','cdi','tdci','cdti','dci','hdi','crdi','jtdm','tdv','d4d']):
        fuel = 'diesel'
    elif any(k in nl for k in ['tfsi','tsi','gdi','mpi','fsi','vtec','vvti']):
        fuel = 'gasoline'
    elif 'electric' in nl:
        fuel = 'electric'
    elif 'hybrid' in nl:
        fuel = 'hybrid'
    power = None
    pm = re.search(r'\b(\d{2,4})\s*(?:hp|hp)\b', name, re.I)
    if pm:
        power = int(pm.group(1))
    yf, yt = parse_year_range(name)
    return engine, fuel, power, yf, yt


_local_products = None


def get_local_products():
    global _local_products
    if _local_products is None:
        _local_products = list(Product.objects.filter(is_active=True).only('id', 'name_lv', 'viscosity', 'sku'))
    return _local_products


def _extract_keywords(name):
    name_up = name.upper()
    visc = re.search(r'\b(\d{1,2}W[-]\d{1,2})\b', name_up)
    visc = visc.group(1) if visc else ''
    specs = re.findall(
        r'\b(?:C\d+|GL[-]?\d+|ATF(?:\s*(?:III|IV|V|VI)\+?)?|\d{3}/\d{3}|SN|CF[-\d]*|SM|CJ[-\d]*|CI[-\d]*|SL|SG|DEXOS\d*|A3B4|A5B5|505\.\d+)\b',
        name_up)
    return visc, set(specs)


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
        score = len(ua_specs & lv_specs)
        if score > 0 or (ua_specs and not lv_specs):
            results.append((score, p))
    results.sort(key=lambda x: -x[0])
    if not results:
        return []
    best = results[0][0]
    if best == 0:
        return [p for _, p in results[:3]]
    return [p for score, p in results if score == best]


def get_engine_products(resp):
    html_val = resp.get('html', {})
    if not html_val:
        return []
    if isinstance(html_val, str):
        try:
            html_val = json.loads(html_val)
        except Exception:
            return []
    result_arr = html_val.get('result_arr', {})
    if not result_arr:
        return []
    out = []
    OIL = {1, 3, 4, 7}
    for sys_name, sys_data in result_arr.items():
        if sys_data.get('component_id', 0) not in OIL:
            continue
        for _, pd in sys_data.get('products', {}).items():
            if not isinstance(pd, dict):
                continue
            for _, pi in pd.items():
                if not isinstance(pi, dict):
                    continue
                name = pi.get('name', '').strip()
                name = re.sub(r'^Motor\s+oil\s+', '', name, flags=re.I).strip()
                name = re.sub(r'[а-яА-ЯіїєёЁ]+.*$', '', name).strip()
                if name:
                    out.append((name, sys_name))
    return out


def run():
    stats = {'mods_new': 0, 'compat_new': 0, 'models_filled': 0, 'api_err': 0}

    missing_count = CarModel.objects.filter(is_active=True, modifications__isnull=True).distinct().count()
    print(f'Modelim bez modifikacijam: {missing_count}')
    if missing_count == 0:
        print('Visi modeli ir aizpilditi!')
        return

    for ua_vt_id, vt_name_en in VEHICLE_TYPES_UA.items():
        vt = VehicleType.objects.filter(name_en=vt_name_en).first()
        if not vt:
            continue

        print(f'\n-- VT{ua_vt_id}: {vt_name_en} --')
        time.sleep(DELAY)
        resp = post_api('getBrands', {'vehicle_type_id': ua_vt_id})
        if not resp:
            print('  ! API kludaa')
            continue
        brands_raw = [(v, t) for v, t in parse_options(resp.get('html', '')) if v != '0']
        print(f'  Brendi: {len(brands_raw)}')

        for brand_ua_id, brand_name in brands_raw:
            # Atrast DB brendu (var but apvienots)
            db_brand = CarBrand.objects.filter(name=brand_name, is_active=True).first()
            if not db_brand:
                clean = re.sub(r'\s*\((?:EU|USA|USA\s*/\s*CAN|CAN|RUS).*?\)\s*$', '', brand_name).strip()
                db_brand = CarBrand.objects.filter(name=clean, is_active=True).first()
            if not db_brand:
                continue

            # Vai šim brendam vispār ir modeli bez modifikacijam?
            has_empty = CarModel.objects.filter(
                brand=db_brand, is_active=True, modifications__isnull=True
            ).distinct().exists()
            if not has_empty:
                continue

            time.sleep(DELAY)
            mresp = post_api('getModels', {'vehicle_type_id': ua_vt_id,
                                           'vehicle_type_make_id': brand_ua_id})
            if not mresp:
                continue
            models_raw = [(v, t) for v, t in parse_options(mresp.get('html', '')) if v != '0']
            if not models_raw:
                continue

            for model_ua_id, model_raw in models_raw:
                clean_name = clean_model_name(model_raw)
                db_model = CarModel.objects.filter(brand=db_brand, name=clean_name).first()
                if not db_model:
                    continue
                if CarModification.objects.filter(car_model=db_model).exists():
                    continue

                time.sleep(DELAY)
                tresp = post_api('getTypes', {
                    'vehicle_type_id': ua_vt_id,
                    'vehicle_type_make_id': brand_ua_id,
                    'vehicle_type_make_model_id': model_ua_id,
                })
                if not tresp:
                    stats['api_err'] += 1
                    continue
                mods_raw = [(v, t) for v, t in parse_options(tresp.get('html', '')) if v != '0']
                if not mods_raw:
                    stats['api_err'] += 1
                    continue

                filled = 0
                for mod_ua_id, mod_name in mods_raw:
                    engine, fuel, power, yf2, yt2 = parse_mod_attrs(mod_name)
                    mod, mc = CarModification.objects.get_or_create(
                        car_model=db_model, name=mod_name,
                        defaults={'engine_volume': engine, 'fuel_type': fuel,
                                  'power_hp': power, 'year_from': yf2,
                                  'year_to': yt2, 'is_active': True}
                    )
                    if mc:
                        stats['mods_new'] += 1
                        filled += 1

                    time.sleep(DELAY)
                    presp = post_api('getProducts', {
                        'vehicle_type_id': ua_vt_id,
                        'vehicle_type_make_id': brand_ua_id,
                        'vehicle_type_make_model_id': model_ua_id,
                        'vehicle_type_make_model_type_id': mod_ua_id,
                    })
                    if presp:
                        for ua_name, _ in get_engine_products(presp):
                            for lp in match_products(ua_name):
                                _, cc = ProductCompatibility.objects.get_or_create(
                                    product=lp, modification=mod,
                                    defaults={'note_lv': '', 'note_ru': '', 'note_en': '', 'note_de': ''})
                                if cc:
                                    stats['compat_new'] += 1

                if filled:
                    stats['models_filled'] += 1
                    remaining = CarModel.objects.filter(is_active=True, modifications__isnull=True).distinct().count()
                    print(f'  OK {db_brand.name} | {clean_name}: {filled} modif. (atliek: {remaining})')

    print(f'\n=== Pabeidzu ===')
    print(f'  Modeli aizpilditi:    {stats["models_filled"]}')
    print(f'  Jaunas modifikacijas: {stats["mods_new"]}')
    print(f'  Jaunas saderibas:     {stats["compat_new"]}')
    print(f'  API kludas:           {stats["api_err"]}')


if __name__ == '__main__':
    run()
