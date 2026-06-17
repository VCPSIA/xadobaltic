import re

with open('rusins_real.html', encoding='utf-8') as f:
    html = f.read()

# Meklē visas <script> tagu URL un inline saturus
print('=== Visi script src ===')
for m in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html):
    print(f'  {m}')

print('\n=== Inline scripts saraksts ===')
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for i, sc in enumerate(scripts):
    sc_stripped = sc.strip()
    if sc_stripped:
        preview = sc_stripped[:80].replace('\n', ' ')
        print(f'Script #{i}: {len(sc_stripped)} chars - {preview}...')

print('\n=== Script ar category-of-equipment ===')
for i, sc in enumerate(scripts):
    if 'category-of-equipment' in sc or 'brand-of-equipment' in sc:
        print(f'\nScript #{i}:')
        print(sc[:5000])
