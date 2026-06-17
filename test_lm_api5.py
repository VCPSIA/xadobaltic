import requests, json, urllib3, sys, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
})

def get(url, **kw):
    return SESSION.get(url, timeout=20, verify=False, **kw)

STATIC = 'https://liquimoly.cloudimg.io/v7/https://www.liqui-moly.com/static/version1781527877/frontend/limo/base'

# Ielādē OWW vehicle service JS
js_files = [
    f'{STATIC}/default/Limo_Search/js/components/oww-vehicle-service.min.js',
    f'{STATIC}/en_GB/Limo_Search/js/components/oww-vehicle-service.min.js',
    f'{STATIC}/default/Limo_Search/js/components/oww-service.min.js',
    f'{STATIC}/default/Oww_JsPlugin/js/oww-plugin.min.js',
]

for js_url in js_files:
    print(f"\n=== {js_url.split('/')[-1]} ===")
    r = get(js_url)
    if r.status_code != 200:
        print(f"  Status: {r.status_code}")
        continue
    js = r.text
    print(f"  Garums: {len(js)}")

    # Meklē API URL
    api_urls = re.findall(r'["\']([^"\']*openapi[^"\']+)["\']', js, re.I)
    for u in api_urls[:5]:
        print(f"  API URL: {u}")

    # Meklē endpoint patterns
    endpoints = re.findall(r'["\'](/api/[^"\']{3,80})["\']', js, re.I)
    for e in endpoints[:10]:
        print(f"  Endpoint: {e}")

    # Meklē parametru nosaukumus
    params = re.findall(r'(?:client_id|clientId|vehicle_type|vehicleType|lang|locale|country)[^"\'<]{0,50}', js)
    for p in set(params[:8]):
        print(f"  Param: {p[:80]}")

    # Meklē fetch/axios calls
    fetches = re.findall(r'fetch\([^)]{0,100}\)', js)
    for f_call in fetches[:5]:
        print(f"  Fetch: {f_call[:100]}")

    # Meklē config/settings objektus
    configs = re.findall(r'(?:config|settings|options)\s*=\s*\{[^}]{0,200}', js)
    for c in configs[:3]:
        print(f"  Config: {c[:150]}")

# Mēģina ar vehicle_type parametru
print("\n\n=== Testē ar vehicle_type ===")
OAPI = 'https://openapi.liqui-moly.com'
tests = [
    '/api/v2/oww/brands?client_id=10&vehicle_type=pkw',
    '/api/v2/oww/brands?client_id=10&type=pkw',
    '/api/v2/oww/brands?client_id=10&lang=en',
    '/api/v2/oww/brands?client_id=10&vehicle=car',
    '/api/v2/oww/brands?client_id=10&country=DE',
]
for ep in tests:
    try:
        r = get(f'{OAPI}{ep}')
        preview = r.text[:300].replace('\n', ' ')
        print(f"\n{ep}")
        print(f"  {r.status_code}: {preview[:200]}")
    except Exception as e:
        print(f"{ep} → ERR: {e}")
