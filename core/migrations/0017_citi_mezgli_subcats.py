from django.db import migrations

SUBCATS = [
    ('Biezās smērvielas',    'bi-droplet-half', 0),
    ('Iekļūstošās smērvielas','bi-wind',        1),
    ('Citi līdzekļi',        'bi-three-dots',   2),
]


def add_subcats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    try:
        parent = NavCategory.objects.get(name_lv='Citi mezgli un mehānismi', tab_slug='passenger-cars')
    except NavCategory.DoesNotExist:
        return
    for name, icon, order in SUBCATS:
        NavCategory.objects.get_or_create(
            parent=parent, name_lv=name,
            defaults={'tab_slug': 'passenger-cars', 'icon': icon, 'order': order, 'is_active': True},
        )


def remove_subcats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    NavCategory.objects.filter(
        name_lv__in=['Biezās smērvielas', 'Iekļūstošās smērvielas', 'Citi līdzekļi'],
        tab_slug='passenger-cars', parent__name_lv='Citi mezgli un mehānismi',
    ).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0016_degviela_subcats')]
    operations = [migrations.RunPython(add_subcats, remove_subcats)]
