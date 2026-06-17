import requests, json, urllib3, sys, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.liqui-moly.com/en/service/oil-guide.html',
})

def get(url, **kw):
    return SESSION.get(url, timeout=20, verify=False, **kw)

OAPI = 'https://openapi.liqui-moly.com'
CLIENT_ID = '10'

# Meklē pareizo endpointu ar client_id
print("=== OWW API ar client_id ===")
tests = [
    f'/api/v2/oww/brands?client_id={CLIENT_ID}',
    f'/api/v2/oww/manufacturers?client_id={CLIENT_ID}',
    f'/api/v2/oww/cars?client_id={CLIENT_ID}',
    f'/api/v1/oww/brands?client_id={CLIENT_ID}',
    f'/api/v2/oww/brand?client_id={CLIENT_ID}',
    f'/api/v2/oww/carbrands?client_id={CLIENT_ID}',
    f'/api/v2/oww/makes?client_id={CLIENT_ID}',
    f'/api/v2/oww/vehiclebrands?client_id={CLIENT_ID}',
    f'/api/v2/oww/carbrand?client_id={CLIENT_ID}',
]
for ep in tests:
    try:
        r = get(f'{OAPI}{ep}')
        ct = r.headers.get('content-type', '')
        preview = r.text[:200].replace('\n', ' ')
        print(f"\n{ep}")
        print(f"  {r.status_code} [{ct[:30]}]")
        print(f"  {preview[:180]}")
    except Exception as e:
        print(f"{ep} → ERR: {e}")

# Meklē OWW JS failu Liqui-Moly lapā
print("\n\n=== Meklē OWW JS requirejs-map ===")
r = get('https://liquimoly.cloudimg.io/v7/https://www.liqui-moly.com/static/version1781527877/frontend/limo/base/en_GB/requirejs-map.min.js?func=proxy&process=minify-js?func=proxy')
js_map = r.text
# Meklē oww / oil-guide-widget
oww_js = re.findall(r'["\'][^"\']*oww[^"\']{0,100}["\']', js_map, re.I)
print(f"OWW JS references ({len(oww_js)}):")
for o in oww_js[:10]:
    print(f"  {o}")

# Meklē arī no requirejs-config
print("\n=== requirejs-config ===")
r2 = get('https://liquimoly.cloudimg.io/v7/https://www.liqui-moly.com/static/version1781527877/frontend/limo/base/en_GB/requirejs-config.min.js?func=proxy&process=minify-js?func=proxy')
js_cfg = r2.text
oww_cfg = re.findall(r'["\'][^"\']*(?:oww|oil.guide|widget)[^"\']{0,100}["\']', js_cfg, re.I)
print(f"OWW config references ({len(oww_cfg)}):")
for o in oww_cfg[:10]:
    print(f"  {o}")

# Visas URLs ar openapi
openapi_refs = re.findall(r'openapi[^"\'<\s]{3,100}', js_cfg, re.I)
openapi_refs += re.findall(r'openapi[^"\'<\s]{3,100}', js_map, re.I)
print(f"\nopenapi references:")
for o in set(openapi_refs[:10]):
    print(f"  {o}")
