from django.db import migrations

SLUG = 'heavy-truckbus'

STRUCTURE = [
    ('Dzesēšanas sistēma', 'bi-thermometer-snow', [
        ('Antifrīzs',            'bi-droplet-fill', 0),
        ('Attīrītāji',           'bi-stars',        1),
        ('Līdzekļi radiatoram',  'bi-filter',       2),
    ]),
    ('Dzinējs', 'bi-gear-wide-connected', [
        ('Attīrītāji',           'bi-stars',             0),
        ('Eļļas',                'bi-droplet-fill',      1),
        ('Metāla kondicionieri', 'bi-shield-check',      2),
        ('Revitalizanti',        'bi-tools',             3),
        ('Citi līdzekļi',        'bi-three-dots',        4),
    ]),
    ('Degvielas sistēma', 'bi-fuel-pump', [
        ('Degvielas piedevas',   'bi-fuel-pump',    0),
        ('Attīrītāji',           'bi-stars',        1),
        ('Revitalizanti',        'bi-tools',        2),
    ]),
    ('Bremžu sistēma', 'bi-octagon', [
        ('Eļļa',                 'bi-droplet-fill', 0),
        ('Apkopes līdzekļi',     'bi-tools',        1),
    ]),
    ('Virsbūve un salons', 'bi-car-front-fill', [
        ('Līdzekļi salona kopšanai',              'bi-brush',     0),
        ('Līdzekļi virsbūves un stiklu kopšanai', 'bi-droplet',   1),
    ]),
    ('Transmisija', 'bi-arrows-angle-contract', [
        ('Eļļas',                'bi-droplet-fill', 0),
        ('Metāla kondicionieri', 'bi-shield-check', 1),
        ('Revitalizanti',        'bi-tools',        2),
        ('Citi līdzekļi',        'bi-three-dots',   3),
    ]),
    ('Stūres sistēma', 'bi-arrow-left-right', [
        ('Revitalizanti',        'bi-tools',        0),
        ('Eļļas',                'bi-droplet-fill', 1),
        ('Citi līdzekļi',        'bi-three-dots',   2),
    ]),
    ('Riepas', 'bi-circle', []),
    ('Citi mezgli un mehānismi', 'bi-three-dots-vertical', [
        ('Biezās smērvielas',     'bi-droplet-half', 0),
        ('Iekļūstošās smērvielas','bi-wind',         1),
        ('Citi līdzekļi',         'bi-three-dots',   2),
    ]),
]


def add_subcats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    for order_idx, (parent_name, parent_icon, children) in enumerate(STRUCTURE):
        parent, _ = NavCategory.objects.get_or_create(
            name_lv=parent_name,
            tab_slug=SLUG,
            parent=None,
            defaults={'icon': parent_icon, 'order': order_idx, 'is_active': True},
        )
        for name, icon, child_order in children:
            NavCategory.objects.get_or_create(
                parent=parent,
                name_lv=name,
                defaults={'tab_slug': SLUG, 'icon': icon, 'order': child_order, 'is_active': True},
            )


def remove_subcats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    NavCategory.objects.filter(tab_slug=SLUG).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0018_bremzu_sistema')]
    operations = [migrations.RunPython(add_subcats, remove_subcats)]
