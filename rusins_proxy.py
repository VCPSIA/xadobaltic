"""
rusins.lv eļļu selektors izmanto PHP proxy uz xado.ua.
Proxy URL: http://rusins.lv/wp-content/themes/generatepress/xado-proxy.php
POST params: proxy_route=getBrands/getModels/getTypes/getProducts, ...
Response: JSON {"html": "..."} vai {"html": {"result_html": "..."}}
"""
import requests, re, json
import urllib3
urllib3.disable_warnings()

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def slow_aes_decrypt(ciphertext_hex, key_hex, iv_hex):
    key = bytes.fromhex(key_hex)
    iv = bytes.fromhex(iv_hex)
    ct = bytes.fromhex(ciphertext_hex)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    dec = cipher.decryptor()
    return dec.update(ct) + dec.finalize()

def get_bypass_session():
    s = requests.Session()
    s.verify = False
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Origin': 'http://rusins.lv',
        'Referer': 'http://rusins.lv/autoserviss-un-apkope/',
    })
    r = s.get('http://rusins.lv/autoserviss-un-apkope/', timeout=30)
    if 'slowAES' in r.text:
        a_m = re.search(r'toNumbers\("([0-9a-f]+)"\),b=', r.text)
        b_m = re.search(r',b=toNumbers\("([0-9a-f]+)"\),c=', r.text)
        c_m = re.search(r',c=toNumbers\("([0-9a-f]+)"\)', r.text)
        if a_m and b_m and c_m:
            cv = slow_aes_decrypt(c_m.group(1), a_m.group(1), b_m.group(1)).hex()
            s.cookies.set('__test', cv, domain='rusins.lv', path='/')
            s.get('http://rusins.lv/autoserviss-un-apkope/?i=1', timeout=30)
            print(f'Bypass veiksmīgs, cookie: {cv[:20]}...')
    return s

PROXY = 'http://rusins.lv/wp-content/themes/generatepress/xado-proxy.php'

s = get_bypass_session()

def xado(route, **params):
    data = {'proxy_route': route, **params}
    r = s.post(PROXY, data=data, timeout=30)
    try:
        return r.json()
    except:
        print(f'Nav JSON: {r.text[:200]}')
        return None

# Test 1: getBrands (vehicle_type_id=1 = Vieglie auto)
print('\n=== getBrands VT=1 ===')
res = xado('getBrands', vehicle_type_id=1)
if res:
    html = res.get('html', '')
    brands = re.findall(r'value="(\d+)"[^>]*>([^<]+)', html)
    print(f'Atrasto marku skaits: {len(brands)}')
    print('Pirmās 10:', brands[:10])
    with open('rusins_brands.json', 'w', encoding='utf-8') as f:
        json.dump(brands, f, ensure_ascii=False, indent=2)
    print('Saglabāts: rusins_brands.json')

# Test 2: getModels (meklē Audi modeli)
if brands:
    audi = next((b for b in brands if 'audi' in b[1].lower()), None)
    if audi:
        print(f'\n=== getModels marka={audi} ===')
        res2 = xado('getModels', vehicle_type_id=1, vehicle_type_make_id=audi[0])
        if res2:
            html2 = res2.get('html', '')
            # Modeļiem ir papildu data atribūti
            models = re.findall(r'value="(\d+)"[^>]*>([^<]+)', html2)
            data_attrs = re.findall(r'<option[^>]+value="(\d+)"([^>]*)>([^<]+)', html2)
            print(f'Modeļu skaits: {len(models)}')
            print('Pirmie 15:', models[:15])
            print('\nAr data atribūtiem:', data_attrs[:3])
