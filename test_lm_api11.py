import requests, urllib3, sys, re, json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Authorization': 'Basic bGltbzpsaW1v',
    'Referer': 'https://www.liqui-moly.com/de/service/oelratgeber.html',
})

def get(url, **kw):
    return SESSION.get(url, timeout=20, verify=False, **kw)

OAPI = 'https://openapi.liqui-moly.com'

# Search API ar auto marku
print("=== Search API testēšana ===")
search_base = f'{OAPI}/api/v2/search/limo_com_de_de/magento2_product_7/DEU/DEU/'
tests = [
    f'{search_base}?q=BMW',
    f'{search_base}?q=volkswagen',
    f'{search_base}?q=5W-30',
    f'{search_base}?q=motor',
    f'{search_base}?q=motoroel&type=oww',
    f'{search_base}suggest?q=BMW',
    f'{search_base}oww?q=BMW',
]
for url in tests:
    r = get(url)
    ct = r.headers.get('content-type','')
    preview = r.text[:400].replace('\n', ' ')
    print(f"\n{url.replace(search_base,'...')}")
    print(f"  {r.status_code} [{ct[:20]}]: {preview[:300]}")

# Skatāmies vai ir OWW konfigurācija atsevišķā JS failā
# Meklē no lapas HTML
print("\n\n=== Meklē OWW komponentes inicializāciju ===")
r = get('https://www.liqui-moly.com/de/service/oelratgeber.html')
html = r.text

# Meklē data-mage-init (cits Magento inicializācijas mehānisms)
mage_inits = re.findall(r'data-mage-init=["\']([^"\']{0,500})["\']', html)
for m in mage_inits[:5]:
    print(f"  data-mage-init: {m[:300]}")

# Meklē OWW widget HTML elementu
oww_widget = re.findall(r'<[^>]*(?:id|class)=["\'][^"\']*oww-vs[^"\']*["\'][^>]*>([\s\S]{0,500})', html)
for w in oww_widget[:3]:
    print(f"\n  oww-vs: {w[:400]}")

# Meklē oww-vehicle-search komponentu
vs_section = re.findall(r'oww-vehicle-search[\s\S]{0,1500}', html)
for vs in vs_section[:1]:
    print(f"\n  vehicle-search:\n{vs[:1500]}")

# Meklē Oww_JsPlugin vai Oww_Search
print("\n=== Oww_JsPlugin references ===")
plugin_refs = re.findall(r'Oww_[A-Za-z]+[^"\'<\s]{0,100}', html)
for p in set(plugin_refs[:10]):
    print(f"  {p[:120]}")
