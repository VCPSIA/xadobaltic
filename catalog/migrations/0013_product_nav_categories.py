from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0012_volume_images'),
        ('core', '0018_bremzu_sistema'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='nav_categories',
            field=models.ManyToManyField(
                blank=True,
                related_name='products',
                to='core.navcategory',
                verbose_name='Navigācijas kategorijas',
            ),
        ),
    ]
