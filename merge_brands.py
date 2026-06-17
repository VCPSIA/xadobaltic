"""
Apvieno reģionālos brendu variantus (EU, USA, RUS, CAN) ar pamatbrendu.
Piemēram: Audi (EU) + Audi (USA) → Audi
"""
import os, django, re
os.environ['DJANGO_SETTINGS_MODULE'] = 'xadobaltic.settings'
import sys; sys.path.insert(0, '.')
django.setup()

from selector.models import CarBrand, CarModel
from django.db import transaction

SUFFIX_RE = re.compile(
    r'\s*\((EU|USA|USA\s*/\s*CAN|CAN|RUS|RU|INT|GLOBAL|AUS|JPN?|GBR?|Daewoo|Bova/Berkhof)\)'
    r'(\s*\(.*?\))*$', re.IGNORECASE
)

def base_name(name):
    return SUFFIX_RE.sub('', name).strip()

# Iegūt visus brendus ar iekavām
regional = CarBrand.objects.filter(name__contains='(').order_by('name')

stats = {'merged': 0, 'renamed': 0, 'skipped': 0}

with transaction.atomic():
    for rb in regional:
        bname = base_name(rb.name)
        if bname == rb.name:
            # Iekavās nav reģiona sufikss (piemēram "Volkswagen (VW)" -> "Volkswagen")
            bname = re.sub(r'\s*\(.*?\)\s*$', '', rb.name).strip()
        if not bname or bname == rb.name:
            stats['skipped'] += 1
            continue

        # Meklēt pamatbrendu
        base = CarBrand.objects.filter(name=bname).exclude(id=rb.id).first()

        if base:
            # Pārcelt modeļus no reģionālā → pamata
            moved = 0
            for model in CarModel.objects.filter(brand=rb):
                # Pārbaudīt vai tāds modelis jau eksistē
                exists = CarModel.objects.filter(brand=base, name=model.name).exists()
                if not exists:
                    model.brand = base
                    model.save()
                    moved += 1
                else:
                    # Modelis jau ir — pārceļam modifikācijas
                    existing = CarModel.objects.filter(brand=base, name=model.name).first()
                    from selector.models import CarModification
                    CarModification.objects.filter(car_model=model).update(car_model=existing)
                    model.delete()

            # Kopēt vehicle_types
            for vt in rb.vehicle_types.all():
                base.vehicle_types.add(vt)

            # Deaktivizēt reģionālo brendu
            rb.is_active = False
            rb.save()

            print(f'  Apvienots: "{rb.name}" → "{base.name}" ({moved} modeļi pārcelti)')
            stats['merged'] += 1

        else:
            # Nav pamata brenda — pārdēvēt šo brendu
            old_name = rb.name
            rb.name = bname
            rb.save()
            print(f'  Pārdēvēts: "{old_name}" → "{bname}"')
            stats['renamed'] += 1

print(f'\nGatavs: {stats["merged"]} apvienoti, {stats["renamed"]} pārdēvēti, {stats["skipped"]} izlaisti')

# Parādīt rezultātu
print('\nAudi brendi pēc apvienošanas:')
for b in CarBrand.objects.filter(name__icontains='audi').order_by('name'):
    mc = CarModel.objects.filter(brand=b).count()
    print(f'  {b.name} (id={b.id}, aktīvs={b.is_active}): {mc} modeļi')
