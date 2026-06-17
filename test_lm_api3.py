import requests, json, urllib3, sys, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
})

def get(url, **kw):
    return SESSION.get(url, timeout=20, verify=False, **kw)

BASE = 'https://www.liqui-moly.com'

# Ielādē oil-guide lapu un meklē OWW widget konfigurāciju
print("=== OWW widget konfigurācija ===")
r = get(f'{BASE}/en/service/oil-guide.html')
html = r.text

# Meklē data- atribūtus
data_attrs = re.findall(r'data-[a-z-]+=["\'](https?://[^"\']+)["\']', html, re.I)
print("data- atribūtu URL:")
for a in data_attrs[:10]:
    print(f"  {a}")

# Meklē "oww" konfigurāciju
oww_config = re.findall(r'oww[^<]{0,500}', html, re.I)
print(f"\nOWW mentions ({len(oww_config)}):")
for o in oww_config[:3]:
    print(f"  {o[:200]}")

# Meklē widget config bloku
widget_config = re.findall(r'window\.[A-Z_]+\s*=\s*\{[^}]{0,500}', html)
print(f"\nwindow config bloki:")
for w in widget_config[:3]:
    print(f"  {w[:300]}")

# Meklē JSON konfigurāciju lapā
json_configs = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', html, re.S)
print(f"\nJSON script tagi: {len(json_configs)}")
for jc in json_configs[:3]:
    print(f"  {jc[:300]}")

# === Testēt openapi.liqui-moly.com ===
print("\n=== openapi.liqui-moly.com ===")
OAPI = 'https://openapi.liqui-moly.com'

# OWW API
oww_tests = [
    '/api/v2/oww/',
    '/api/v2/oww/brands',
    '/api/v2/oww/manufacturers',
    '/api/v1/oww/brands',
    '/api/v2/vehicle/brands',
    '/api/v2/vehicle/',
    '/api/v2/cars/brands',
    '/api/v1/cars/',
    '/api/oww/brands',
]
for ep in oww_tests:
    try:
        r = get(f'{OAPI}{ep}')
        ct = r.headers.get('content-type', '')
        preview = r.text[:150].replace('\n', ' ')
        print(f"{ep} → {r.status_code} [{ct[:25]}] {preview[:100]}")
    except Exception as e:
        print(f"{ep} → ERR: {e}")

# Pamēģinājums ar Liqui-Moly DE oil guide (šis varētu būt savādāk strukturēts)
print("\n=== LM DE oil guide ===")
r_de = get('https://www.liqui-moly.com/de/service/oelratgeber.html')
html_de = r_de.text

oww_de = re.findall(r'oww-url[^<]{0,200}', html_de, re.I)
for o in oww_de[:3]:
    print(f"  {o[:200]}")

data_de = re.findall(r'data-(?:oww|api|url)[^<]{0,100}', html_de, re.I)
for d in data_de[:5]:
    print(f"  data: {d[:150]}")
