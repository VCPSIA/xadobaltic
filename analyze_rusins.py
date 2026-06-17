import requests, re, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'lv-LV,lv;q=0.9,en;q=0.8',
}

s = requests.Session()
r = s.get('https://rusins.lv/autoserviss-un-apkope/', headers=headers, timeout=30)
print(f'Status: {r.status_code}')

html = r.text

# Meklē AJAX URL
ajax_patterns = [
    r'url\s*:\s*["\']([^"\']+)["\']',
    r'fetch\s*\(\s*["\']([^"\']+)["\']',
    r'axios\.[a-z]+\s*\(\s*["\']([^"\']+)["\']',
    r'wp-admin/admin-ajax\.php',
    r'action\s*:\s*["\']([^"\']+)["\']',
    r'admin_url\s*\(\s*["\']([^"\']+)["\']',
    r'ajaxurl\s*=\s*["\']([^"\']+)["\']',
    r'["\']action["\']:\s*["\']([^"\']+)["\']',
]

print('\n=== AJAX patterns ===')
for pat in ajax_patterns:
    matches = re.findall(pat, html)
    if matches:
        print(f'Pattern: {pat[:50]}')
        for m in set(matches[:10]):
            print(f'  {m}')

# Meklē script tags
print('\n=== Script URLs ===')
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
for sc in scripts:
    if any(x in sc for x in ['oil', 'elja', 'selector', 'ajax', 'custom', 'rusins', 'main', 'app']):
        print(f'  {sc}')

print('\n=== Inline script ar "oil" vai "elja" vai "ajax" ===')
inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for sc in inline_scripts:
    if any(x in sc.lower() for x in ['oil', 'ajax', 'action', 'kategorija', 'marka', 'auto']):
        print(sc[:3000])
        print('---')

print('\n=== ajaxurl vai admin_ajax ===')
if 'ajaxurl' in html:
    idx = html.find('ajaxurl')
    print(html[max(0,idx-100):idx+300])

if 'admin-ajax' in html:
    idx = html.find('admin-ajax')
    print(html[max(0,idx-100):idx+300])
