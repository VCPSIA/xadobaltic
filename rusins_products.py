import sys, io, requests, re, json
import urllib3
urllib3.disable_warnings()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def aes_decrypt(ct_hex, key_hex, iv_hex):
    key, iv, ct = bytes.fromhex(key_hex), bytes.fromhex(iv_hex), bytes.fromhex(ct_hex)
    c = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    d = c.decryptor()
    return (d.update(ct) + d.finalize()).hex()

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

PROXY = 'http://rusins.lv/wp-content/themes/generatepress/xado-proxy.php'

def post(route, **p):
    r = s.post(PROXY, data={'proxy_route': route, **p}, timeout=30)
    return r.json() if r.status_code == 200 else None

# Audi EU, A3 S3 8P modelis (id=2399)
model_id = '2399'
make_id = '26'
vt_id = '1'

# getTypes
types_r = post('getTypes', vehicle_type_id=vt_id, vehicle_type_make_id=make_id,
               vehicle_type_make_model_id=model_id)
if types_r:
    types_html = types_r['html']
    types = re.findall(r"<option[^>]*value='(\d+)'([^>]*)>([^<]+)", types_html)
    print(f'Types priekš Audi A3 8P: {len(types)}')
    for val, attrs, name in types[:5]:
        print(f'  {val}: {name.strip()}')

    if types:
        # Izlaiž id=0 placeholder
        real_types = [(v, a, n) for v, a, n in types if v != '0']
        if real_types:
            tv, ta, tn = real_types[0]
            mm_m = re.search(r"data-vehicle_type_make_model_id='(\d+)'", ta)
            mm_id = mm_m.group(1) if mm_m else model_id

            print(f'\ngetProducts: vt={vt_id}, make={make_id}, model={mm_id}, type={tv}')
            prod_r = post('getProducts',
                          vehicle_type_id=vt_id,
                          vehicle_type_make_id=make_id,
                          vehicle_type_make_model_id=mm_id,
                          vehicle_type_make_model_type_id=tv)
            if prod_r:
                with open('rusins_products_sample.json', 'w', encoding='utf-8') as f:
                    json.dump(prod_r, f, ensure_ascii=False, indent=2)
                print('Saglabāts: rusins_products_sample.json')

                html = prod_r.get('html', {})
                if isinstance(html, dict):
                    rh = html.get('result_html', '')
                    print(f'\nresult_html struktūra ({len(rh)} chars):')
                    # Meklē produktu grupas
                    groups = re.findall(r'<h[23][^>]*>([^<]+)</h[23]>', rh)
                    print('Grupas:', groups[:20])
                    # Meklē produktu nosaukumus
                    products_in_html = re.findall(r'class="[^"]*product[^"]*"[^>]*>[^<]*<[^>]+>([^<]+)', rh)
                    print('Produkti:', products_in_html[:10])
                    print('\nHTML (pirmie 3000):')
                    print(rh[:3000])
