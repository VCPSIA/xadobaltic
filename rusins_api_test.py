"""
Mēģina atrast rusins.lv API endpoints bez browser.
Izmantojam Chrome cookie, ko iegūstam caur registry/profile.
"""
import requests, json, re
import urllib3
urllib3.disable_warnings()

# Chrome cookies rusins.lv - jāiegūst manuāli vai ar CDP
# Pagaidām mēģina REST API bez cookies

s = requests.Session()
s.verify = False
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest',
})

base = 'http://rusins.lv'

endpoints = [
    # WordPress REST API
    '/wp-json/wp/v2/',
    '/wp-json/rusins/v1/brands',
    '/wp-json/rusins/v1/cars',
    # Admin AJAX
    '/wp-admin/admin-ajax.php',
    # Common plugin endpoints
    '/wp-json/oil-selector/v1/brands',
    '/wp-json/vehicle-selector/v1/brands',
    '/wp-json/car-service/v1/brands',
]

print('=== REST API pārbaude ===')
for ep in endpoints:
    url = base + ep
    try:
        r = s.get(url, timeout=15)
        print(f'GET {ep}: {r.status_code} ({len(r.text)} chars)')
        if r.status_code == 200 and len(r.text) < 1000:
            print(f'  Saturs: {r.text[:200]}')
    except Exception as e:
        print(f'GET {ep}: KĻŪDA - {type(e).__name__}: {str(e)[:50]}')

print('\n=== AJAX POST pārbaudes ===')
ajax_url = base + '/wp-admin/admin-ajax.php'
actions = ['get_brands', 'get_car_brands', 'oil_selector_brands', 'elja_brands',
           'get_makes', 'get_vehicle_brands', 'car_oil_brands', 'rusins_brands',
           'get_car_types', 'oil_get_brands']
for action in actions:
    try:
        r = s.post(ajax_url, data={'action': action}, timeout=10)
        if r.status_code == 200 and r.text not in ['-1', '0', '']:
            print(f'action={action}: {r.status_code} -> {r.text[:200]}')
    except Exception as e:
        pass

print('\nPabeigts.')
