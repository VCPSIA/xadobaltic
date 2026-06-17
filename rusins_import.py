"""
Importē VT1 (vieglie auto) modeļu modifikācijas un produktu saderību
no rusins.lv proxy (kas savukārt proxy uz xado.ua).

Priekšrocība pār tiešo xado.ua: nav session rate-limit problēmas.
"""
import os, sys, re, time, json, io
import django, requests, urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility
from catalog.models import VehicleType, Product
import xado_ua_import as ua  # parse helpers

PROXY = 'http://rusins.lv/wp-content/themes/generatepress/xado-proxy.php'
DELAY = 0.5

# ─── AES bypass ──────────────────────────────────────────────────────────────

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def aes_decrypt(ct_hex, key_hex, iv_hex):
    key, iv, ct = bytes.fromhex(key_hex), bytes.fromhex(iv_hex), bytes.fromhex(ct_hex)
    c = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    d = c.decryptor()
    return (d.update(ct) + d.finalize()).hex()

def make_session():
    s = requests.Session()
    s.verify = False
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, */*',
        'Referer': 'http://rusins.lv/autoserviss-un-apkope/',
    })
    r = s.get('http://rusins.lv/autoserviss-un-apkope/', timeout=30)
    m = re.search(r'toNumbers\("([0-9a-f]+)"\),b=toNumbers\("([0-9a-f]+)"\),c=toNumbers\("([0-9a-f]+)"\)', r.text)
    if m:
        cv = aes_decrypt(m.group(3), m.group(1), m.group(2))
        s.cookies.set('__test', cv, domain='rusins.lv', path='/')
        s.get('http://rusins.lv/autoserviss-un-apkope/?i=1', timeout=30)
        print('Session OK')
    return s

sess = make_session()

def xado(route, retries=3, **p):
    for _ in range(retries):
        try:
            r = sess.post(PROXY, data={'proxy_route': route, **p}, timeout=30)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            time.sleep(1)
    return None

# ─── PARSERS ─────────────────────────────────────────────────────────────────

def parse_options(html):
    soup = BeautifulSoup(html or '', 'html.parser')
    return [(o['value'], o.get_text(strip=True), o.attrs)
            for o in soup.find_all('option') if o.get('value') and o['value'] != '0']

def parse_products_html(html):
    """Parses rusins.lv getProducts HTML → list of product names."""
    soup = BeautifulSoup(html or '', 'html.parser')
    names = []
    for dd in soup.find_all('dd'):
        txt = dd.get_text(strip=True)
        # Produktu nosaukumi satur 'XADO' vai 'Motor oil' vai viscosity
        if txt and ('XADO' in txt or re.search(r'\d+W[-–]\d+', txt)):
            names.append(txt)
    return list(set(names))

# ─── STATISTIKA ──────────────────────────────────────────────────────────────

stats = {'new_mods': 0, 'new_compat': 0, 'fixed_models': 0, 'skipped': 0}
vt1 = VehicleType.objects.get(slug='passenger-cars')

# ─── GALVENAIS PROCESS ───────────────────────────────────────────────────────

print('=== RUSINS.LV IMPORT: VT1 modifikācijas ===\n')

# Iegūst visas rusins.lv markas
brands_res = xado('getBrands', vehicle_type_id=1)
if not brands_res:
    print('KĻŪDA: nevar iegūt markas')
    sys.exit(1)

rusins_brands = parse_options(brands_res['html'])
print(f'rusins.lv markas: {len(rusins_brands)}\n')

total_brands = len(rusins_brands)
for bi, (brand_id, brand_name, _) in enumerate(rusins_brands):
    # Meklē šo marku mūsu DB
    db_brand = CarBrand.objects.filter(name=brand_name, vehicle_types=vt1).first()
    if not db_brand:
        stats['skipped'] += 1
        continue

    # Modeļi bez modifikācijām
    no_mods = list(CarModel.objects.filter(
        brand=db_brand, modifications__isnull=True
    ).distinct())

    if not no_mods:
        continue

    pct = int((bi + 1) / total_brands * 100)
    print(f'[{pct:3d}%] {brand_name}: {len(no_mods)} modeļi bez modif.', flush=True)

    # Iegūst modeļus no rusins.lv
    time.sleep(DELAY)
    mres = xado('getModels', vehicle_type_id=1, vehicle_type_make_id=brand_id)
    if not mres:
        print(f'       ! getModels kļūda')
        continue

    rusins_models = parse_options(mres['html'])
    # Karte: tīrs nosaukums → (rusins_id, pilns_nosaukums)
    model_map = {}
    for mid, mname, _ in rusins_models:
        clean = ua.clean_model_name(mname)
        model_map[clean] = mid
        model_map[mname.strip()] = mid  # arī ar gadu

    for db_model in no_mods:
        rusins_id = model_map.get(db_model.name) or model_map.get(ua.clean_model_name(db_model.name))
        if not rusins_id:
            print(f'       ~ {db_model.name!r}: nav rusins atbilstības')
            continue

        time.sleep(DELAY)
        tres = xado('getTypes', vehicle_type_id=1,
                    vehicle_type_make_id=brand_id,
                    vehicle_type_make_model_id=rusins_id)
        if not tres:
            continue

        mods_list = parse_options(tres['html'])
        if not mods_list:
            print(f'       0  {db_model.name!r}: getTypes tukšs')
            continue

        new_for_model = 0
        for mod_id, mod_name, _ in mods_list:
            engine, fuel, power, yf, yt = ua.parse_mod_attrs(mod_name)
            mod, created = CarModification.objects.get_or_create(
                car_model=db_model, name=mod_name,
                defaults={'engine_volume': engine, 'fuel_type': fuel,
                          'power_hp': power, 'year_from': yf, 'year_to': yt,
                          'is_active': True}
            )
            if created:
                stats['new_mods'] += 1
                new_for_model += 1

            # Produktu saderība
            time.sleep(DELAY * 0.8)
            pres = xado('getProducts',
                        vehicle_type_id=1,
                        vehicle_type_make_id=brand_id,
                        vehicle_type_make_model_id=rusins_id,
                        vehicle_type_make_model_type_id=mod_id)
            if not pres:
                continue

            html_data = pres.get('html', {})
            if isinstance(html_data, dict):
                result_html = html_data.get('result_html', '')
            else:
                result_html = ''

            if result_html:
                product_names = parse_products_html(result_html)
                for pname in product_names:
                    for lp in ua.match_products(pname):
                        _, c = ProductCompatibility.objects.get_or_create(
                            product=lp, modification=mod)
                        if c:
                            stats['new_compat'] += 1

        if new_for_model > 0:
            stats['fixed_models'] += 1
            print(f'       + {db_model.name!r}: +{new_for_model} modif.', flush=True)

print(f'\n=== PABEIGTS ===')
print(f'  Laboti modeļi:        {stats["fixed_models"]}')
print(f'  Jaunas modifikācijas: {stats["new_mods"]}')
print(f'  Jaunas saderības:     {stats["new_compat"]}')
print(f'  Izlaistas markas:     {stats["skipped"]}')
