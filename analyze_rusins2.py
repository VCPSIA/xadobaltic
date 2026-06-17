import re

with open('rusins_real.html', encoding='utf-8') as f:
    html = f.read()

print(f'HTML garums: {len(html)}\n')

# Meklē visu kas saistīts ar eļļu selektoru
print('=== EĻĻAS atlase HTML ===')
idx = html.lower().find('elļ')
if idx == -1:
    idx = html.lower().find('ellas')
if idx == -1:
    idx = html.lower().find('atlase')
print(html[max(0,idx-200):idx+2000])

print('\n\n=== Visi <select> elementi ===')
for m in re.findall(r'<select[^>]*>.*?</select>', html, re.DOTALL):
    if len(m) < 2000:
        print(m[:500])
        print('---')

print('\n\n=== Script pirksti uz marka/modelis/tips ===')
for sc in re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
    if any(x in sc.lower() for x in ['marka', 'modelis', 'kategorija', 'oil', 'fluid']):
        print(sc[:3000])
        print('===')

print('\n\n=== Formas ===')
for m in re.findall(r'<form[^>]*>.*?</form>', html, re.DOTALL):
    print(m[:1000])
    print('---')
