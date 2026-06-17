import requests, re
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

def solve_and_get(s, url):
    r = s.get(url, timeout=30)
    if 'slowAES' in r.text:
        a_m = re.search(r'toNumbers\("([0-9a-f]+)"\),b=', r.text)
        b_m = re.search(r',b=toNumbers\("([0-9a-f]+)"\),c=', r.text)
        c_m = re.search(r',c=toNumbers\("([0-9a-f]+)"\)', r.text)
        if a_m and b_m and c_m:
            cookie_val = slow_aes_decrypt(c_m.group(1), a_m.group(1), b_m.group(1)).hex()
            s.cookies.set('__test', cookie_val, domain='rusins.lv', path='/')
            redir_url = re.search(r'location\.href="([^"]+)"', r.text)
            if redir_url:
                r = s.get(redir_url.group(1), timeout=30)
    return r

s = requests.Session()
s.verify = False
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'http://rusins.lv/autoserviss-un-apkope/',
})

# Iegūst service-prices.js
js_url = 'http://rusins.lv/wp-content/themes/generatepress/service-prices.js'
print(f'Iegūst: {js_url}')
r = solve_and_get(s, js_url)
print(f'Status: {r.status_code}, garums: {len(r.text)}')

if r.status_code == 200 and len(r.text) > 500:
    with open('service-prices.js', 'w', encoding='utf-8') as f:
        f.write(r.text)
    print('Saglabāts: service-prices.js')
    print('\nPirmās 5000 rindas:')
    print(r.text[:5000])
else:
    print('Saturs:', r.text[:300])

    # Mēģina citus failu nosaukumus
    for name in ['oil-selector.js', 'car-selector.js', 'custom.js', 'scripts.js', 'main.js']:
        url2 = f'http://rusins.lv/wp-content/themes/generatepress/{name}'
        r2 = s.get(url2, timeout=15)
        if r2.status_code == 200 and 'slowAES' not in r2.text and len(r2.text) > 100:
            print(f'Atrasts: {url2} ({len(r2.text)} chars)')
            with open(name, 'w', encoding='utf-8') as f:
                f.write(r2.text)
