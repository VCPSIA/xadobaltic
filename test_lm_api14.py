import requests, urllib3, sys, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Accept-Language': 'de-DE,de;q=0.9',
})

def get(url, **kw):
    return SESSION.get(url, timeout=20, verify=False, **kw)

# 1. Meklē window.mmsoww_ mainīgos DE lapā
print("=== window.mmsoww_* mainīgie ===")
# Vispirms iegūst DE/DE oil guide
r = get('https://www.liqui-moly.com/de/de/service/oelratgeber.html')
html = r.text
print(f"Status: {r.status_code}, garums: {len(html)}")

mmsoww = re.findall(r'mmsoww[_\w]+\s*=\s*["\'][^"\']{0,100}["\']', html)
for m in mmsoww[:20]:
    print(f"  {m}")

mmsoww2 = re.findall(r'window\.mmsoww[^;]{0,150}', html)
for m in mmsoww2[:10]:
    print(f"  {m}")

# 2. Skatās OWW plugin buildUrl() pilno kodu
print("\n=== oww-plugin.min.js pilns kods ===")
V = 'version1781527877'
CDN_BASE = f'https://liquimoly.cloudimg.io/v7/https://www.liqui-moly.com/static/{V}/frontend/Magento/base/default'
r_js = get(f'{CDN_BASE}/Oww_JsPlugin/js/oww-plugin.min.js?func=proxy&process=minify-js')
js = r_js.text
print(js)

# 3. Skatās oww-utils.min.js pilnu kodu
print("\n=== oww-utils.min.js pilns kods ===")
r_utils = get(f'{CDN_BASE}/Limo_Search/js/oww-utils.min.js?func=proxy&process=minify-js')
print(r_utils.text)
