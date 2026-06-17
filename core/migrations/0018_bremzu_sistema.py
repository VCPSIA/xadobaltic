from django.db import migrations


def update(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    # Pārdēvē kategoriju
    NavCategory.objects.filter(
        name_lv='Kondicionēšanas sistēma', tab_slug='passenger-cars'
    ).update(
        name_lv='Bremžu sistēma',
        icon='bi-octagon',
    )
    # Pievieno apakškategorijas
    try:
        parent = NavCategory.objects.get(name_lv='Bremžu sistēma', tab_slug='passenger-cars')
    except NavCategory.DoesNotExist:
        return
    for name, icon, order in [('Eļļa', 'bi-droplet-fill', 0), ('Apkopes līdzekļi', 'bi-tools', 1)]:
        NavCategory.objects.get_or_create(
            parent=parent, name_lv=name,
            defaults={'tab_slug': 'passenger-cars', 'icon': icon, 'order': order, 'is_active': True},
        )


def revert(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    NavCategory.objects.filter(
        name_lv__in=['Eļļa', 'Apkopes līdzekļi'],
        tab_slug='passenger-cars', parent__name_lv='Bremžu sistēma',
    ).delete()
    NavCategory.objects.filter(
        name_lv='Bremžu sistēma', tab_slug='passenger-cars'
    ).update(name_lv='Kondicionēšanas sistēma', icon='bi-wind')


class Migration(migrations.Migration):
    dependencies = [('core', '0017_citi_mezgli_subcats')]
    operations = [migrations.RunPython(update, revert)]
