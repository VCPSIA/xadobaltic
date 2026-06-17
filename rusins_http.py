import requests, re
import urllib3
urllib3.disable_warnings()

s = requests.Session()
s.verify = False

# Pārbaude ar http://
urls = [
    'http://rusins.lv/autoserviss-un-apkope/',
    'https://rusins.lv/autoserviss-un-apkope/',
]

for url in urls:
    try:
        print(f'Mēģina: {url}')
        r = s.get(url, timeout=60, verify=False,
                  headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120'})
        print(f'OK! Status={r.status_code}, garums={len(r.text)}')

        html = r.text
        # Saglabā HTML
        with open('rusins_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print('Saglabāts: rusins_page.html')

        # Meklē AJAX
        print('\n--- admin-ajax ---')
        for m in re.findall(r'.{0,100}admin[-_]ajax.{0,100}', html):
            print(m)

        print('\n--- ajaxurl ---')
        for m in re.findall(r'.{0,100}ajaxurl.{0,100}', html):
            print(m)

        print('\n--- action ---')
        for m in re.findall(r'"action"\s*:\s*"([^"]+)"', html):
            print(m)

        print('\n--- Script src ---')
        for sc in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html):
            if any(x in sc for x in ['custom', 'oil', 'elja', 'auto', 'ajax', 'main', 'script']):
                print(sc)
        break
    except Exception as e:
        print(f'Kļūda: {e}')
