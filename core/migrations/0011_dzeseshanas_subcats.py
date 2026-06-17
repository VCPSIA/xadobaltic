from django.db import migrations


SUBCATS = [
    ('Antifrīzs',           'bi-droplet-half', 0),
    ('Attīrītāji',          'bi-stars',        1),
    ('Līdzekļi radiatoram', 'bi-thermometer',  2),
]


def add_subcats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    try:
        parent = NavCategory.objects.get(name_lv='Dzesēšanas sistēma', tab_slug='passenger-cars')
    except NavCategory.DoesNotExist:
        return
    for name, icon, order in SUBCATS:
        NavCategory.objects.get_or_create(
            parent=parent,
            name_lv=name,
            defaults={
                'tab_slug': 'passenger-cars',
                'icon': icon,
                'order': order,
                'is_active': True,
            },
        )


def remove_subcats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    NavCategory.objects.filter(
        name_lv__in=['Antifrīzs', 'Attīrītāji', 'Līdzekļi radiatoram'],
        tab_slug='passenger-cars',
    ).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0010_navcategory_parent')]
    operations = [migrations.RunPython(add_subcats, remove_subcats)]
