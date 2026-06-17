import requests, json, urllib3, sys, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
})

BASE = 'https://www.liqui-moly.com'

def get(url, **kw):
    return SESSION.get(url, timeout=20, verify=False, **kw)

# Ielādē oil-guide lapu un meklē oww JS failu
print("=== Ielādē oil-guide lapu ===")
r = get(f'{BASE}/en/service/oil-guide.html')
html = r.text

# Meklē oww (oil widget web?) JS failu
oww_files = re.findall(r'(https?://[^"\']*oww[^"\']*\.js[^"\']*)', html, re.I)
print(f"OWW JS faili: {oww_files[:5]}")

# Meklē visus JS failus
all_js = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', html)
print(f"\nVisi JS faili ({len(all_js)}):")
for f in all_js[:10]:
    print(f"  {f}")

# Meklē tiešos API URL
api_patterns = re.findall(r'["\'](/[^"\']*(?:api|oww)[^"\']{3,50})["\']', html, re.I)
print(f"\nAPI patterri HTML:")
for p in set(api_patterns[:15]):
    print(f"  {p}")

# Meklē "apiUrl" konfigurāciju
api_url_config = re.findall(r'apiUrl["\s:\']+([^"\'<\s]+)', html, re.I)
print(f"\napiUrl config: {api_url_config[:5]}")

# Ielādē pirmo no oww JS failiem
if oww_files:
    print(f"\n=== Analizē OWW JS failu ===")
    js_url = oww_files[0]
    rjs = get(js_url)
    js = rjs.text
    print(f"JS garums: {len(js)} baiti")

    # Meklē API URL patterri
    api_finds = re.findall(r'["\']([^"\']{5,80}(?:api|brand|model|manufactur|vehicle)[^"\']{3,80})["\']', js, re.I)
    print(f"\nAPI URL atrašanās:")
    shown = set()
    for f in api_finds:
        if f not in shown and not f.startswith('//') and len(f) < 100:
            print(f"  {f}")
            shown.add(f)
        if len(shown) >= 20:
            break

# Mēģina tiešos URL no oww widget
print("\n=== Testa oww endpointi ===")
test_endpoints = [
    '/en/service/oil-guide/api/',
    '/en/gb/service/oil-guide/api/',
    '/oww/api/brands',
    '/oww/brands',
    '/en/oww/brands',
    '/rest/V1/oww/brands',
    '/rest/default/V1/oww/brands',
    '/api/oww/car-brands',
    '/graphql',
]
for ep in test_endpoints:
    try:
        r = get(f'{BASE}{ep}')
        ct = r.headers.get('content-type', '')
        preview = r.text[:120].replace('\n', ' ')
        print(f"{ep} → {r.status_code} [{ct[:30]}] {preview[:80]}")
    except Exception as e:
        print(f"{ep} → ERR: {e}")
