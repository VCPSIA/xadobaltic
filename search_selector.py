with open('rusins_real.html', encoding='utf-8') as f:
    html = f.read()

# Meklē ap category-of-equipment
idx = html.find('category-of-equipment')
print('=== Ap category-of-equipment ===')
print(html[max(0,idx-500):idx+3000])

# Meklē AJAX vai fetch
import re
print('\n\n=== fetch() vai $.ajax ===')
for m in re.findall(r'.{0,200}(fetch\(|\.ajax\(|\$\.get\(|\$\.post\().{0,400}', html, re.DOTALL):
    print(m[:500])
    print('---')

# Apskata visu selektora sadaļu ap html
print('\n\n=== HTML ap selector-container ===')
idx2 = html.find('selector-container')
print(html[max(0,idx2-200):idx2+3000])
