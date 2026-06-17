"""
Iegūst rusins.lv cookies no Chrome SQLite datubāzes.
"""
import sqlite3, json, shutil, os, base64, requests
import urllib3
urllib3.disable_warnings()

# Chrome atslēga (AES-256-GCM ar DPAPI)
def get_chrome_key():
    local_state = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Local State')
    with open(local_state, 'r', encoding='utf-8') as f:
        ls = json.load(f)
    encrypted_key = base64.b64decode(ls['os_crypt']['encrypted_key'])
    encrypted_key = encrypted_key[5:]  # Noņem DPAPI prefix

    import ctypes, ctypes.wintypes
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', ctypes.wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_char))]

    p = ctypes.create_string_buffer(encrypted_key, len(encrypted_key))
    blobin = DATA_BLOB(len(encrypted_key), p)
    blobout = DATA_BLOB()
    ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blobin), None, None, None, None, 0, ctypes.byref(blobout))
    key = ctypes.string_at(blobout.pbData, blobout.cbData)
    return key

def decrypt_cookie(key, encrypted_value):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        nonce = encrypted_value[3:15]
        ciphertext = encrypted_value[15:]
        return AESGCM(key).decrypt(nonce, ciphertext, None).decode('utf-8')
    except:
        # Vecāks Chrome - DPAPI tieši
        import ctypes
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [('cbData', ctypes.wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_char))]
        p = ctypes.create_string_buffer(encrypted_value, len(encrypted_value))
        blobin = DATA_BLOB(len(encrypted_value), p)
        blobout = DATA_BLOB()
        ctypes.windll.crypt32.CryptUnprotectData(
            ctypes.byref(blobin), None, None, None, None, 0, ctypes.byref(blobout))
        return ctypes.string_at(blobout.pbData, blobout.cbData).decode('utf-8')

# Datubāze
cookie_paths = [
    os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network\Cookies'),
    os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies'),
]

print('Meklē Chrome cookies...')
key = get_chrome_key()
print(f'Chrome atslēga iegūta: {len(key)} baiti')

cookies = {}
for cp in cookie_paths:
    if not os.path.exists(cp):
        continue
    print(f'Atver: {cp}')
    # Kopē (Chrome var bloķēt)
    tmp = cp + '.tmp'
    shutil.copy2(cp, tmp)
    conn = sqlite3.connect(tmp)
    cur = conn.execute(
        "SELECT name, encrypted_value, value FROM cookies WHERE host_key LIKE '%rusins%'")
    for name, enc_val, val in cur.fetchall():
        if enc_val and enc_val[:3] == b'v10':
            val = decrypt_cookie(key, enc_val)
        cookies[name] = val
        print(f'  Cookie: {name}={val[:50]}')
    conn.close()
    os.unlink(tmp)
    break

print(f'\nKopā {len(cookies)} cookies rusins.lv')

if not cookies:
    print('Nav cookies! Pārlūkā jāapmeklē rusins.lv vismaz vienu reizi.')
else:
    # Tagad mēģina piekļūt lapai ar šiem cookies
    s = requests.Session()
    s.verify = False
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    })
    for name, val in cookies.items():
        s.cookies.set(name, val, domain='rusins.lv')

    print('\nMēģina piekļūt ar cookies...')
    try:
        r = s.get('http://rusins.lv/autoserviss-un-apkope/', timeout=30)
        print(f'Status: {r.status_code}, garums: {len(r.text)}')
        if len(r.text) > 1000:
            with open('rusins_real.html', 'w', encoding='utf-8') as f:
                f.write(r.text)
            print('Saglabāts: rusins_real.html')
            # Meklē API
            import re
            print('\n--- AJAX/API atsauces ---')
            for m in re.findall(r'.{0,50}(ajax|admin-ajax|action|wp-json|api).{0,50}', r.text, re.I):
                print(m)
        else:
            print('Joprojām aizsargāts:', r.text[:200])
    except Exception as e:
        print(f'Kļūda: {e}')
