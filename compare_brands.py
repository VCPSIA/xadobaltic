import os, sys, io, requests, re
import urllib3
urllib3.disable_warnings()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

from selector.models import CarBrand
from catalog.models import VehicleType
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from bs4 import BeautifulSoup

def aes_decrypt(ct_hex, key_hex, iv_hex):
    key, iv, ct = bytes.fromhex(key_hex), bytes.fromhex(iv_hex), bytes.fromhex(ct_hex)
    c = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    d = c.decryptor()
    return (d.update(ct) + d.finalize()).hex()

s = requests.Session()
s.verify = False
s.headers.update({'User-Agent': 'Mozilla/5.0', 'X-Requested-With': 'XMLHttpRequest'})
r = s.get('http://rusins.lv/autoserviss-un-apkope/', timeout=30)
m = re.search(r'toNumbers\("([0-9a-f]+)"\),b=toNumbers\("([0-9a-f]+)"\),c=toNumbers\("([0-9a-f]+)"\)', r.text)
cv = aes_decrypt(m.group(3), m.group(1), m.group(2))
s.cookies.set('__test', cv, domain='rusins.lv', path='/')
s.get('http://rusins.lv/autoserviss-un-apkope/?i=1', timeout=30)

r2 = s.post('http://rusins.lv/wp-content/themes/generatepress/xado-proxy.php',
            data={'proxy_route': 'getBrands', 'vehicle_type_id': 1}, timeout=30)
soup = BeautifulSoup(r2.json()['html'], 'html.parser')
rusins_brands = {o.get_text(strip=True) for o in soup.find_all('option') if o.get('value') and o['value'] != '0'}

vt1 = VehicleType.objects.get(slug='passenger-cars')
db_brands = set(CarBrand.objects.filter(vehicle_types=vt1).values_list('name', flat=True))

print(f'rusins.lv: {len(rusins_brands)} markas')
print(f'DB: {len(db_brands)} markas')

missing_in_db = rusins_brands - db_brands
in_db_not_rusins = db_brands - rusins_brands

print(f'\nTrūkst DB ({len(missing_in_db)}):')
for b in sorted(missing_in_db):
    print(f'  {b}')

print(f'\nDB bet ne rusins ({len(in_db_not_rusins)}):')
for b in sorted(in_db_not_rusins):
    print(f'  {b}')
