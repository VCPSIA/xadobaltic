"""Izdrukā visas rusins.lv VT1 markas un atrod trūkstošās DB markas."""
import sys, io, re, requests, time
import urllib3
urllib3.disable_warnings()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from bs4 import BeautifulSoup
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def aes_decrypt(ct_hex, key_hex, iv_hex):
    key, iv, ct = bytes.fromhex(key_hex), bytes.fromhex(iv_hex), bytes.fromhex(ct_hex)
    c = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    d = c.decryptor()
    return (d.update(ct) + d.finalize()).hex()

s = requests.Session(); s.verify = False
s.headers.update({'User-Agent':'Mozilla/5.0','X-Requested-With':'XMLHttpRequest',
                  'Referer':'http://rusins.lv/autoserviss-un-apkope/'})
r = s.get('http://rusins.lv/autoserviss-un-apkope/', timeout=30)
m = re.search(r'toNumbers\("([0-9a-f]+)"\),b=toNumbers\("([0-9a-f]+)"\),c=toNumbers\("([0-9a-f]+)"\)', r.text)
cv = aes_decrypt(m.group(3), m.group(1), m.group(2))
s.cookies.set('__test', cv, domain='rusins.lv', path='/')
s.get('http://rusins.lv/autoserviss-un-apkope/?i=1', timeout=30)
PROXY = 'http://rusins.lv/wp-content/themes/generatepress/xado-proxy.php'

brands_r = s.post(PROXY, data={'proxy_route':'getBrands','vehicle_type_id':1}, timeout=30)
soup = BeautifulSoup(brands_r.json()['html'], 'html.parser')
brands = [(o['value'], o.get_text(strip=True)) for o in soup.find_all('option')
          if o.get('value') and o['value']!='0']

print(f'=== Visas {len(brands)} rusins.lv VT1 markas ===')
for bid, bname in sorted(brands, key=lambda x: x[1]):
    print(f'  id={bid}: "{bname}"')

# Meklē DB markas
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','xadobaltic.settings')
import sys as _sys; _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()
from selector.models import CarBrand, CarModel

rusins_names = {bname for _, bname in brands}

print('\n=== DB markas ar modifikācijām trūkst → rusins.lv atbilstība ===')
for b in CarBrand.objects.all().order_by('name'):
    cnt = CarModel.objects.filter(brand=b, modifications__isnull=True).count()
    if cnt == 0:
        continue
    # Meklē rusins
    found = [rn for rn in rusins_names if b.name in rn or rn.startswith(b.name)]
    print(f'  "{b.name}" ({cnt} bez modif.) → rusins: {found if found else "NAV"}')
