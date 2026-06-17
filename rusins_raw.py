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
    return cipher.decryptor().update(ct) + cipher.decryptor().finalize()

s = requests.Session()
s.verify = False
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
    'Origin': 'http://rusins.lv',
    'Referer': 'http://rusins.lv/autoserviss-un-apkope/',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
})

# Bypass
r = s.get('http://rusins.lv/autoserviss-un-apkope/', timeout=30)
a_m = re.search(r'toNumbers\("([0-9a-f]+)"\),b=', r.text)
b_m = re.search(r',b=toNumbers\("([0-9a-f]+)"\),c=', r.text)
c_m = re.search(r',c=toNumbers\("([0-9a-f]+)"\)', r.text)
cv = slow_aes_decrypt(c_m.group(1), a_m.group(1), b_m.group(1)).hex()
s.cookies.set('__test', cv, domain='rusins.lv', path='/')
s.get('http://rusins.lv/autoserviss-un-apkope/?i=1', timeout=30)

PROXY = 'http://rusins.lv/wp-content/themes/generatepress/xado-proxy.php'

# Raw POST un skatās atbildi
r2 = s.post(PROXY, data={'proxy_route': 'getBrands', 'vehicle_type_id': '1'}, timeout=30)
print(f'Status: {r2.status_code}')
print(f'Content-Type: {r2.headers.get("Content-Type", "?")}')
print(f'Response garums: {len(r2.text)}')
print(f'Response (pirmie 1000): {r2.text[:1000]}')
