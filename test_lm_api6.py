import requests, json, urllib3, sys, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.liqui-moly.com/en/service/oil-guide.html',
})

def get(url, **kw):
    return SESSION.get(url, timeout=30, verify=False, **kw)

V = 'version1781527877'
CDN = f'https://liquimoly.cloudimg.io/v7/https://www.liqui-moly.com/static/{V}/frontend/limo/base'
DIRECT = f'https://www.liqui-moly.com/static/{V}/frontend/limo/base'

# Mēģina ar CDN URL formātu
print("=== OWW JS failu meklēšana ===")
js_candidates = [
    f'{CDN}/default/Oww_JsPlugin/js/oww-plugin.min.js?func=proxy&process=minify-js',
    f'{CDN}/default/Limo_Search/js/components/oww-vehicle-service.min.js?func=proxy&process=minify-js',
    f'{CDN}/default/Limo_Search/js/components/oww-service.min.js?func=proxy&process=minify-js',
    f'{CDN}/default/Oww_Search/js/alpine-loader.min.js?func=proxy&process=minify-js',
    f'{DIRECT}/default/Oww_JsPlugin/js/oww-plugin.min.js',
    f'{DIRECT}/default/Limo_Search/js/components/oww-vehicle-service.min.js',
]

found_js = {}
for url in js_candidates:
    r = get(url)
    name = url.split('/')[-1].split('?')[0]
    print(f"{name}: {r.status_code} ({len(r.text)} baiti)")
    if r.status_code == 200 and len(r.text) > 100:
        found_js[name] = r.text

# Analizē atrastos JS failus
for name, js in found_js.items():
    print(f"\n=== Analizē: {name} ===")
    # API URL
    api_urls = re.findall(r'["\']https?://openapi[^"\']{3,150}["\']', js)
    for u in api_urls[:5]:
        print(f"  API URL: {u}")
    # Endpoints
    eps = re.findall(r'["\'][`]?/api/[^"\'`]{3,80}["\']', js)
    for e in set(eps[:10]):
        print(f"  Endpoint: {e}")
    # Parametri
    pars = re.findall(r'(?:clientId|client_id|vehicleId|vehicle_id|brandId|brand_id)[^;]{0,60}', js)
    for p in set(pars[:5]):
        print(f"  Param: {p[:80]}")
    # Drukā pirmos 500 rakstzīmes
    print(f"  Preview: {js[:500]}")

# Ja neko neatrada, meklē citādā vietā
if not found_js:
    print("\n=== Meklē OWW API atsevišķā domēnā ===")
    oww_tests = [
        'https://oww.liqui-moly.com/api/brands',
        'https://oww.liqui-moly.com/brands',
        'https://oww-api.liqui-moly.com/brands',
        'https://oilguide.liqui-moly.com/api/brands',
        'https://openapi.liqui-moly.com/api/v2/oww/brands?client_id=10&format=json',
        'https://openapi.liqui-moly.com/api/v2/oww/manufacturers?client_id=10&format=json',
    ]
    for u in oww_tests:
        try:
            r = get(u)
            print(f"{u}\n  → {r.status_code}: {r.text[:200].replace(chr(10), ' ')}")
        except Exception as e:
            print(f"{u} → {e}")
