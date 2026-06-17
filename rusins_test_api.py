import requests, re, json
import urllib3
urllib3.disable_warnings()

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
    return s

PROXY = 'http://rusins.lv/wp-content/themes/generatepress/xado-proxy.php'
s = make_session()

def xado(route, **p):
    r = s.post(PROXY, data={'proxy_route': route, **p}, timeout=30)
    return r.json() if r.status_code == 200 else None

# Iegūst Audi (EU) ID
brands_res = xado('getBrands', vehicle_type_id=1)
brands_html = brands_res['html']
brands = re.findall(r"value='(\d+)'[^>]*>([^<]+)", brands_html)
print(f'Kopā {len(brands)} markas')

audi_eu = next((b for b in brands if b[1].strip() == 'Audi (EU)'), None)
print(f'Audi EU: {audi_eu}')

# getModels priekš Audi EU
if audi_eu:
    brand_id = audi_eu[0]
    models_res = xado('getModels', vehicle_type_id=1, vehicle_type_make_id=brand_id)
    models_html = models_res['html']
    # Iegūst visus modeļus ar data atribūtiem
    models = re.findall(r"<option[^>]*value='(\d+)'([^>]*)>([^<]+)", models_html)
    print(f'\nAudi EU modeļi ({len(models)}):')
    for val, attrs, name in models[:20]:
        print(f'  id={val} {attrs.strip()} -> {name.strip()}')

    if models:
        # Iegūst types priekš pirmā modeļa
        first_model = models[0]
        model_id = first_model[0]
        attrs = first_model[1]
        type_id_m = re.search(r"data-type-id='(\d+)'", attrs)
        make_id_m = re.search(r"data-vehicle_type_make_id='(\d+)'", attrs)
        type_id = type_id_m.group(1) if type_id_m else '1'
        make_id = make_id_m.group(1) if make_id_m else brand_id

        print(f'\ngetTypes model_id={model_id}, type_id={type_id}, make_id={make_id}')
        types_res = xado('getTypes', vehicle_type_id=type_id,
                         vehicle_type_make_id=make_id,
                         vehicle_type_make_model_id=model_id)
        if types_res:
            types_html = types_res['html']
            types = re.findall(r"<option[^>]*value='(\d+)'([^>]*)>([^<]+)", types_html)
            print(f'Types ({len(types)}):')
            for val, attrs2, name in types[:5]:
                print(f'  id={val} {attrs2.strip()} -> {name.strip()}')

            if types:
                # getProducts priekš pirmā tipa
                first_type = types[0]
                type_val = first_type[0]
                attrs2 = first_type[1]
                make_model_id_m = re.search(r"data-vehicle_type_make_model_id='(\d+)'", attrs2)
                make_model_id = make_model_id_m.group(1) if make_model_id_m else model_id

                print(f'\ngetProducts type_id={type_id}, make_id={make_id}, model_id={make_model_id}, type_val={type_val}')
                prod_res = xado('getProducts',
                                vehicle_type_id=type_id,
                                vehicle_type_make_id=make_id,
                                vehicle_type_make_model_id=make_model_id,
                                vehicle_type_make_model_type_id=type_val)
                if prod_res:
                    print(f'getProducts atbilde: {json.dumps(prod_res, ensure_ascii=False)[:3000]}')
                    with open('rusins_products_sample.json', 'w', encoding='utf-8') as f:
                        json.dump(prod_res, f, ensure_ascii=False, indent=2)
                    print('\nSaglabāts: rusins_products_sample.json')
