import os, sys, io, re, requests, time
import urllib3
urllib3.disable_warnings()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

from selector.models import CarBrand, CarModel
from bs4 import BeautifulSoup
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def aes_decrypt(ct_hex, key_hex, iv_hex):
    key, iv, ct = bytes.fromhex(key_hex), bytes.fromhex(iv_hex), bytes.fromhex(ct_hex)
    c = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    d = c.decryptor()
    return (d.update(ct) + d.finalize()).hex()

s = requests.Session()
s.verify = False
s.headers.update({'User-Agent': 'Mozilla/5.0', 'X-Requested-With': 'XMLHttpRequest',
                  'Referer': 'http://rusins.lv/autoserviss-un-apkope/'})
r = s.get('http://rusins.lv/autoserviss-un-apkope/', timeout=30)
m = re.search(r'toNumbers\("([0-9a-f]+)"\),b=toNumbers\("([0-9a-f]+)"\),c=toNumbers\("([0-9a-f]+)"\)', r.text)
cv = aes_decrypt(m.group(3), m.group(1), m.group(2))
s.cookies.set('__test', cv, domain='rusins.lv', path='/')
s.get('http://rusins.lv/autoserviss-un-apkope/?i=1', timeout=30)

PROXY = 'http://rusins.lv/wp-content/themes/generatepress/xado-proxy.php'

# Iegūst visas rusins.lv markas ar ID
brands_r = s.post(PROXY, data={'proxy_route': 'getBrands', 'vehicle_type_id': 1}, timeout=30)
brands_html = brands_r.json()['html']
soup = BeautifulSoup(brands_html, 'html.parser')
rusins_brand_map = {o.get_text(strip=True): o['value']
                   for o in soup.find_all('option') if o.get('value') and o['value'] != '0'}

# Pārbauda problēmmarkas
problem_brands = ['Ford (EU)', 'Mercedes-Benz (EU)', 'Nissan (EU)', 'Dodge (USA / CAN)',
                  'Chrysler (EU)', 'Chrysler (USA / CAN)', 'Mitsubishi (EU)']

for brand_name in problem_brands:
    rusins_id = rusins_brand_map.get(brand_name)
    if not rusins_id:
        print(f'\n{brand_name}: NAV rusins.lv sarakstā!')
        continue

    # DB modeļi bez modif.
    try:
        db_brand = CarBrand.objects.get(name=brand_name)
    except CarBrand.DoesNotExist:
        print(f'\n{brand_name}: NAV DB!')
        continue

    db_no_mods = list(CarModel.objects.filter(
        brand=db_brand, modifications__isnull=True
    ).distinct().values_list('name', flat=True))

    if not db_no_mods:
        continue

    # rusins.lv modeļi
    time.sleep(0.5)
    mods_r = s.post(PROXY, data={'proxy_route': 'getModels', 'vehicle_type_id': 1,
                                  'vehicle_type_make_id': rusins_id}, timeout=30)
    msoup = BeautifulSoup(mods_r.json()['html'], 'html.parser')
    rusins_models = [o.get_text(strip=True) for o in msoup.find_all('option')
                     if o.get('value') and o['value'] != '0']

    print(f'\n=== {brand_name} ===')
    print(f'DB bez modif.: {len(db_no_mods)}')
    print(f'rusins.lv modeļi: {len(rusins_models)}')
    print(f'\nDB:')
    for n in db_no_mods[:8]:
        print(f'  "{n}"')
    print(f'rusins.lv:')
    for n in rusins_models[:8]:
        print(f'  "{n}"')
