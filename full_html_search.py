with open('rusins_real.html', encoding='utf-8') as f:
    html = f.read()

# Meklē $.post kontekstu
idx = html.find('$.post')
if idx >= 0:
    print('=== $.post konteksts ===')
    print(html[max(0,idx-500):idx+1000])

# Meklē category-of-equipment onChange
print('\n\n=== category change ===')
idx2 = html.find('category-of-equipment')
# Atrod visas atsauces
import re
for m in re.finditer('category.of.equipment', html):
    print(f'\nAtrodas pie {m.start()}:')
    print(html[max(0,m.start()-200):m.end()+500])
    print('---')

# Izdrukā visu HTML beigās (pēc FOOTER) kur ir JS
print('\n\n=== HTML beigas (pēdējie 5000 chars) ===')
print(html[-5000:])
