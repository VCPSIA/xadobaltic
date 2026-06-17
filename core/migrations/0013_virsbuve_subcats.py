from django.db import migrations

SUBCATS = [
    ('Līdzekļi salona kopšanai',              'bi-car-front',  0),
    ('Līdzekļi virsbūves un stiklu kopšanai', 'bi-droplet',    1),
]


def add_subcats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    try:
        parent = NavCategory.objects.get(name_lv='Virsbūve un salons', tab_slug='passenger-cars')
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
        name_lv__in=['Līdzekļi salona kopšanai', 'Līdzekļi virsbūves un stiklu kopšanai'],
        tab_slug='passenger-cars', parent__isnull=False,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0012_dzineja_subcats')]
    operations = [migrations.RunPython(add_subcats, remove_subcats)]
