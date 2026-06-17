"""
Labo atlikušās markas: Dodge, Mitsubishi, Infiniti, Mazda + citas kas vēl nav labotas.
Tieši uzdod DB marku → rusins.lv marku mapings.
"""
import os, sys, re, time, io
import django, requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility
from catalog.models import Product
import xado_ua_import as ua

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

PROXY = 'http://rusins.lv/wp-content/themes/generatepress/xado-proxy.php'
DELAY = 0.5

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
    for attempt in range(retries):
        try:
            r = sess.post(PROXY, data={'proxy_route': route, **p}, timeout=30)
            if r.status_code == 200:
                j = r.json()
                return j
            print(f'  [HTTP {r.status_code}] {route}', flush=True)
        except Exception as e:
            print(f'  [kļūda attempt {attempt+1}] {route}: {e}', flush=True)
            time.sleep(2)
    return None

def parse_options(html):
    soup = BeautifulSoup(html or '', 'html.parser')
    return [(o['value'], o.get_text(strip=True), o.attrs)
            for o in soup.find_all('option') if o.get('value') and o['value'] != '0']

def parse_products_html(html):
    soup = BeautifulSoup(html or '', 'html.parser')
    names = []
    for dd in soup.find_all('dd'):
        txt = dd.get_text(strip=True)
        if txt and ('XADO' in txt or re.search(r'\d+W[-–]\d+', txt)):
            names.append(txt)
    return list(set(names))

def normalize(name):
    n = name.lower()
    n = re.sub(r'\([\d\s\-–\.]+\)', '', n)
    n = re.sub(r'[^a-z0-9\s]', ' ', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

# Iegūst rusins.lv brand map ar id
brands_r = xado('getBrands', vehicle_type_id=1)
rusins_brand_soup = BeautifulSoup(brands_r['html'], 'html.parser')
rusins_brand_map = {o.get_text(strip=True): o['value']
                   for o in rusins_brand_soup.find_all('option')
                   if o.get('value') and o['value'] != '0'}
print(f'rusins.lv markas: {len(rusins_brand_map)}')

# Tieši definēts mapings: DB marka → rusins.lv marku saraksts
BRAND_MAP = {
    'Dodge':      ['Dodge (EU)', 'Dodge (USA / CAN)'],
    'Mitsubishi': ['Mitsubishi (EU)', 'Mitsubishi (USA / CAN)'],
    'Infiniti':   ['Infiniti (EU)', 'Infiniti (USA)'],
    'Mazda':      ['Mazda (EU)', 'Mazda (USA / CAN)'],
    # Atlikušās no iepriekšējiem startiem
    'Chrysler':   ['Chrysler (EU)', 'Chrysler (USA / CAN)'],
    'Ford':       ['Ford (EU)', 'Ford (USA)'],
    'Mercedes-Benz': ['Mercedes-Benz (EU)', 'Mercedes-Benz (USA / CAN)'],
    'Nissan':     ['Nissan (EU)', 'Nissan (USA / CAN)'],
    'Kia':        ['Kia (EU)', 'Kia (USA / CAN)'],
    'Opel':       ['Opel'],
}

stats = {'fixed': 0, 'new_mods': 0, 'new_compat': 0}

for db_name, rusins_names in BRAND_MAP.items():
    try:
        db_brand = CarBrand.objects.get(name=db_name)
    except CarBrand.DoesNotExist:
        print(f'\n{db_name}: nav DB → izlaižam')
        continue

    no_mods = list(CarModel.objects.filter(
        brand=db_brand, modifications__isnull=True).distinct())
    if not no_mods:
        print(f'\n{db_name}: visi modeļi jau laboti ✓')
        continue

    # Iegūst rusins.lv model sarakstu no visām šīs markas variācijām
    all_rusins_models = []
    for rn in rusins_names:
        rid = rusins_brand_map.get(rn)
        if not rid:
            print(f'  [{rn}]: nav rusins.lv sarakstā')
            continue
        time.sleep(DELAY)
        mr = xado('getModels', vehicle_type_id=1, vehicle_type_make_id=rid)
        if not mr:
            print(f'  [{rn}]: getModels kļūda')
            continue
        models = parse_options(mr['html'])
        print(f'  [{rn}]: {len(models)} modeļi', flush=True)
        for mid, mname, mattrs in models:
            all_rusins_models.append((rid, mid, mname, mattrs))

    if not all_rusins_models:
        print(f'\n{db_name}: nav rusins modeļu → izlaižam')
        continue

    print(f'\n{db_name}: {len(no_mods)} bez modif., {len(all_rusins_models)} rusins modeļi')

    for db_model in no_mods:
        # Precīzs match
        exact_id = None
        rusins_bid = None
        for rid, mid, mname, _ in all_rusins_models:
            clean = ua.clean_model_name(mname)
            if clean == db_model.name or mname.strip() == db_model.name:
                exact_id = mid
                rusins_bid = rid
                break

        if exact_id:
            rusins_mid = exact_id
        else:
            # Fuzzy
            db_norm = normalize(db_model.name)
            db_words = set(db_norm.split())
            best_id = None; best_score = 0; best_bid = None
            for rid, mid, mname, _ in all_rusins_models:
                r_words = set(normalize(mname).split())
                common = db_words & r_words
                if not common: continue
                score = len(common) / max(len(db_words), len(r_words))
                if score > best_score:
                    best_score = score; best_id = mid; best_bid = rid
            rusins_mid = best_id if best_score >= 0.5 else None
            rusins_bid = best_bid

        if not rusins_mid:
            print(f'  ~ "{db_model.name}": nav atbilstības')
            continue

        match_name = next((mname for _, mid, mname, _ in all_rusins_models if mid == rusins_mid), '?')
        match_type = 'precīzi' if exact_id else 'fuzzy'
        print(f'  → "{db_model.name}" [{match_type}] ↔ "{match_name}"')

        time.sleep(DELAY)
        tres = xado('getTypes', vehicle_type_id=1,
                    vehicle_type_make_id=rusins_bid,
                    vehicle_type_make_model_id=rusins_mid)
        if not tres:
            print(f'    getTypes kļūda')
            continue
        mods_list = parse_options(tres['html'])
        if not mods_list:
            print(f'    0 getTypes tukšs')
            continue

        new_for_model = 0
        for mod_id, mod_name, _ in mods_list:
            engine, fuel, power, yf, yt = ua.parse_mod_attrs(mod_name)
            mod, created = CarModification.objects.get_or_create(
                car_model=db_model, name=mod_name,
                defaults={'engine_volume': engine, 'fuel_type': fuel,
                          'power_hp': power, 'year_from': yf, 'year_to': yt, 'is_active': True}
            )
            if created:
                stats['new_mods'] += 1
                new_for_model += 1

            time.sleep(DELAY * 0.6)
            pres = xado('getProducts', vehicle_type_id=1,
                        vehicle_type_make_id=rusins_bid,
                        vehicle_type_make_model_id=rusins_mid,
                        vehicle_type_make_model_type_id=mod_id)
            if pres:
                html_data = pres.get('html', {})
                rh = html_data.get('result_html', '') if isinstance(html_data, dict) else ''
                for pname in parse_products_html(rh):
                    for lp in ua.match_products(pname):
                        _, c = ProductCompatibility.objects.get_or_create(product=lp, modification=mod)
                        if c: stats['new_compat'] += 1

        if new_for_model > 0:
            stats['fixed'] += 1
            print(f'    + {new_for_model} modif.', flush=True)

print(f'\n=== PABEIGTS ===')
print(f'  Laboti:      {stats["fixed"]}')
print(f'  Jaunas mod:  {stats["new_mods"]}')
print(f'  Jaunas sader.: {stats["new_compat"]}')
