import requests, urllib3, sys, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
})

def get(url, **kw):
    return SESSION.get(url, timeout=30, verify=False, **kw)

V = 'version1781527877'
# Pareizais ceļš: frontend/Magento/base/default/
CDN_BASE = f'https://liquimoly.cloudimg.io/v7/https://www.liqui-moly.com/static/{V}/frontend/Magento/base/default'
DIRECT_BASE = f'https://www.liqui-moly.com/static/{V}/frontend/Magento/base/default'

print("=== OWW JS failu ielāde ===")
js_modules = [
    'Oww_JsPlugin/js/oww-plugin.min.js',
    'Oww_Search/js/alpine-loader.min.js',
    'Limo_Search/js/components/oww-vehicle-service.min.js',
    'Limo_Search/js/components/oww-service.min.js',
    'Limo_Search/js/components/oww-suggest-service.min.js',
    'Limo_Search/js/oww-utils.min.js',
]

found = {}
for mod in js_modules:
    name = mod.split('/')[-1]
    # Mēģina CDN URL
    r = get(f'{CDN_BASE}/{mod}?func=proxy&process=minify-js')
    if r.status_code == 200 and len(r.text) > 50:
        print(f"CDN OK: {name} ({len(r.text)} b)")
        found[name] = r.text
        continue
    # Mēģina tiešo URL
    r2 = get(f'{DIRECT_BASE}/{mod}')
    if r2.status_code == 200 and len(r2.text) > 50:
        print(f"DIRECT OK: {name} ({len(r2.text)} b)")
        found[name] = r2.text
    else:
        print(f"MISS: {name} → CDN:{r.status_code}, DIRECT:{r2.status_code}")

# Analizē atrastos failus
for name, js in found.items():
    print(f"\n{'='*60}")
    print(f"=== {name} ===")
    print(f"Garums: {len(js)}")

    # Meklē API URL
    api_urls = re.findall(r'["\`\'](https?://[^"\`\']{10,150})["\`\']', js)
    print("API URLs:")
    for u in set(api_urls[:10]):
        print(f"  {u}")

    # Meklē endpoint patterns
    eps = re.findall(r'["\'`](/[a-z][^"\`\']{3,80})["\`\']', js)
    api_eps = [e for e in eps if any(x in e for x in ['api', 'brand', 'model', 'car', 'vehicle', 'oww'])]
    if api_eps:
        print("Endpoints:")
        for e in set(api_eps[:15]):
            print(f"  {e}")

    # Drukā pirmos 800 chars
    print(f"JS preview:")
    print(js[:800])
