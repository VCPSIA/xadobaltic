"""
Importē modifikācijas modeļiem kuriem tās trūkst (VT1).
Atjauno HTTP sesiju katrai markai lai izvairītos no rate-limit.
Run: venv\Scripts\python.exe xado_fix_nomods.py
"""
import os, sys, time, requests, urllib3
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

import xado_ua_import as imp
from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility
from catalog.models import VehicleType

urllib3.disable_warnings()

BASE = 'https://xado.ua'
DELAY = 0.6
UA_VT_ID = 1

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer': 'https://xado.ua/ua/',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}

def new_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    s.verify = False
    return s

def post(session, route, data, retries=4):
    url = f'{BASE}/index.php?route=information/oil_selection/{route}'
    for attempt in range(retries):
        try:
            r = session.post(url, data=data, timeout=25)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            if attempt == retries - 1:
                print(f'    ! {route} kludda: {e}')
            time.sleep(1.5)
    return None

stats = {'mods': 0, 'compat': 0, 'fixed': 0}

print(f'=== Fix: modeļi bez modifikācijām (VT{UA_VT_ID}) ===\n')

vt = VehicleType.objects.get(slug='passenger-cars')

# Iegūst xado.ua brand sarakstu ar jaunu sesiju
sess = new_session()
resp = post(sess, 'getBrands', {'vehicle_type_id': UA_VT_ID})
brands_raw = [(v, t) for v, t in imp.parse_options(resp.get('html', '')) if v != '0']
print(f'Markas: {len(brands_raw)}\n')

for bi, (ua_brand_id, brand_name) in enumerate(brands_raw):
    db_brand = CarBrand.objects.filter(name=brand_name).first()
    if not db_brand:
        continue

    no_mod_qs = CarModel.objects.filter(brand=db_brand, modifications__isnull=True).distinct()
    if not no_mod_qs.exists():
        continue

    no_mod_list = list(no_mod_qs)
    pct = int((bi + 1) / len(brands_raw) * 100)
    print(f'[{pct:3d}%] {brand_name}: {len(no_mod_list)} modeļi bez modif', flush=True)

    # Jauna sesija katrai markai
    sess = new_session()
    time.sleep(DELAY)

    mresp = post(sess, 'getModels', {'vehicle_type_id': UA_VT_ID, 'vehicle_type_make_id': ua_brand_id})
    if not mresp:
        print(f'       ! getModels kludda')
        continue
    models_raw = [(v, t) for v, t in imp.parse_options(mresp.get('html', '')) if v != '0']
    ua_model_map = {imp.clean_model_name(t): v for v, t in models_raw}

    for db_model in no_mod_list:
        ua_model_id = ua_model_map.get(db_model.name)
        if not ua_model_id:
            print(f'       ~ {db_model.name!r}: nav xado.ua atbilstibas')
            continue

        time.sleep(DELAY)
        tresp = post(sess, 'getTypes', {
            'vehicle_type_id': UA_VT_ID,
            'vehicle_type_make_id': ua_brand_id,
            'vehicle_type_make_model_id': ua_model_id,
        })
        if not tresp:
            continue
        mods_raw = [(v, t) for v, t in imp.parse_options(tresp.get('html', '')) if v != '0']
        if not mods_raw:
            print(f'       0  {db_model.name!r}: getTypes tukss')
            continue

        new_for_model = 0
        for mod_ua_id, mod_name in mods_raw:
            engine, fuel, power, yf2, yt2 = imp.parse_mod_attrs(mod_name)
            mod, created = CarModification.objects.get_or_create(
                car_model=db_model, name=mod_name,
                defaults={'engine_volume': engine, 'fuel_type': fuel,
                          'power_hp': power, 'year_from': yf2, 'year_to': yt2,
                          'is_active': True}
            )
            if created:
                stats['mods'] += 1
                new_for_model += 1

            time.sleep(DELAY)
            presp = post(sess, 'getProducts', {
                'vehicle_type_id': UA_VT_ID,
                'vehicle_type_make_id': ua_brand_id,
                'vehicle_type_make_model_id': ua_model_id,
                'vehicle_type_make_model_type_id': mod_ua_id,
            })
            if not presp:
                continue
            for ua_name, _ in imp.get_engine_products_from_response(presp):
                for lp in imp.match_products(ua_name):
                    _, c = ProductCompatibility.objects.get_or_create(
                        product=lp, modification=mod,
                        defaults={'note_lv': '', 'note_ru': '', 'note_en': '', 'note_de': ''}
                    )
                    if c:
                        stats['compat'] += 1

        if new_for_model > 0:
            stats['fixed'] += 1
            print(f'       + {db_model.name!r}: {new_for_model} modif, {stats["compat"]} sader. kopā', flush=True)

print(f'\n=== Pabeigts ===')
print(f'  Laboti modeļi:        {stats["fixed"]}')
print(f'  Jaunas modifikācijas: {stats["mods"]}')
print(f'  Jaunas saderības:     {stats["compat"]}')
