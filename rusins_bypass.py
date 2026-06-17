"""
Atrisina rusins.lv slowAES bot protection challenge.
Implementē AES-CBC atšifrēšanu Python.
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
    plain = dec.update(ct) + dec.finalize()
    return plain.hex()

s = requests.Session()
s.verify = False
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
})

def solve_challenge(html):
    # Meklē a, b, c vērtības
    a_m = re.search(r'toNumbers\("([0-9a-f]+)"\),b=', html)
    b_m = re.search(r',b=toNumbers\("([0-9a-f]+)"\),c=', html)
    c_m = re.search(r',c=toNumbers\("([0-9a-f]+)"\)', html)
    if not (a_m and b_m and c_m):
        return None
    a, b, c = a_m.group(1), b_m.group(1), c_m.group(1)
    print(f'  a={a}, b={b}, c={c}')
    cookie_val = slow_aes_decrypt(c, a, b)
    print(f'  cookie_val={cookie_val}')
    return cookie_val

# 1. solis: iegūst challenge
print('1. Iegūst challenge...')
r1 = s.get('http://rusins.lv/autoserviss-un-apkope/', timeout=30)
print(f'Status: {r1.status_code}, garums: {len(r1.text)}')

cookie_val = solve_challenge(r1.text)
if not cookie_val:
    print('Neizdevās atrast AES vērtības!')
    print(r1.text[:500])
    exit()

# 2. solis: uzstāda cookie un dod redirect
s.cookies.set('__test', cookie_val, domain='rusins.lv', path='/')
print(f'\n2. Cookie uzstādīts: __test={cookie_val}')

# 3. solis: seko redirect
r2 = s.get('http://rusins.lv/autoserviss-un-apkope/?i=1', timeout=30)
print(f'Redirect status: {r2.status_code}, garums: {len(r2.text)}')

if len(r2.text) > 2000:
    with open('rusins_real.html', 'w', encoding='utf-8') as f:
        f.write(r2.text)
    print('Saglabāts: rusins_real.html')

    print('\n--- Script tags ---')
    for m in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', r2.text):
        print(f'  {m}')

    print('\n--- AJAX ---')
    for m in re.findall(r'.{0,100}(admin.ajax|ajaxurl|\.ajax|wp-json).{0,100}', r2.text):
        print(f'  {m}')

    print('\n--- Inline scripts ar ajax/action ---')
    for sc in re.findall(r'<script[^>]*>(.*?)</script>', r2.text, re.DOTALL):
        if 'ajax' in sc.lower() or 'action' in sc.lower():
            print(sc[:2000])
            print('---')
else:
    print('Joprojām aizsargāts!')
    # Varbūt ir vairāki redirecti
    if 'toNumbers' in r2.text:
        print('Vēl viens challenge...')
        cookie_val2 = solve_challenge(r2.text)
        if cookie_val2:
            s.cookies.set('__test', cookie_val2, domain='rusins.lv', path='/')
            r3 = s.get('http://rusins.lv/autoserviss-un-apkope/?i=1', timeout=30)
            print(f'R3 status: {r3.status_code}, garums: {len(r3.text)}')
            if len(r3.text) > 2000:
                with open('rusins_real.html', 'w', encoding='utf-8') as f:
                    f.write(r3.text)
                print('Saglabāts: rusins_real.html')
    else:
        print(r2.text[:300])
