from django.db import migrations

CATS = [
    ('Revitalizants',            'bi-tools',    0),
    ('Ieroču kopšanas līdzekļi', 'bi-shield',   1),
]


def add_cats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    for name, icon, order in CATS:
        NavCategory.objects.get_or_create(
            name_lv=name, tab_slug='ieroci', parent=None,
            defaults={'icon': icon, 'order': order, 'is_active': True},
        )


def remove_cats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    NavCategory.objects.filter(
        tab_slug='ieroci', parent__isnull=True,
        name_lv__in=[c[0] for c in CATS],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0025_motorcycle_cats')]
    operations = [migrations.RunPython(add_cats, remove_cats)]
