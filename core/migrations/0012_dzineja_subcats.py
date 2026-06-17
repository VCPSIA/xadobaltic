from django.db import migrations

SUBCATS = [
    ('Attīrītāji',          'bi-stars',             0),
    ('Eļļas',               'bi-droplet-fill',      1),
    ('Metāla kondicionieri', 'bi-shield-check',      2),
    ('Revitalizanti',       'bi-tools',             3),
    ('Citi līdzekļi',       'bi-three-dots',        4),
]


def add_subcats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    try:
        parent = NavCategory.objects.get(name_lv='Dzinējs', tab_slug='passenger-cars')
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
        name_lv__in=['Attīrītāji', 'Eļļas', 'Metāla kondicionieri', 'Revitalizanti', 'Citi līdzekļi'],
        tab_slug='passenger-cars', parent__isnull=False,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0011_dzeseshanas_subcats')]
    operations = [migrations.RunPython(add_subcats, remove_subcats)]
