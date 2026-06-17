from django.db import migrations

SUBCATS = [
    ('Eļļas',               'bi-droplet-fill', 0),
    ('Metāla kondicionieri', 'bi-shield-check', 1),
    ('Revitalizanti',       'bi-tools',        2),
    ('Citi līdzekļi',       'bi-three-dots',   3),
]


def add_subcats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    try:
        parent = NavCategory.objects.get(name_lv='Transmisija', tab_slug='passenger-cars')
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
        name_lv__in=['Eļļas', 'Metāla kondicionieri', 'Revitalizanti', 'Citi līdzekļi'],
        tab_slug='passenger-cars', parent__name_lv='Transmisija',
    ).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0013_virsbuve_subcats')]
    operations = [migrations.RunPython(add_subcats, remove_subcats)]
