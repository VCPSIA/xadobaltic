from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

CUSTOMER_TYPE = [
    ('private', 'Privāts pircējs'),
    ('company', 'Uzņēmums / Juridiska persona'),
]

COUNTRY_CHOICES = [
    ('LV', 'Latvija'),
    ('LT', 'Lietuva'),
    ('EE', 'Igaunija'),
    ('FI', 'Somija'),
    ('SE', 'Zviedrija'),
    ('DE', 'Vācija'),
    ('PL', 'Polija'),
    ('OTHER', 'Cita'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    customer_type = models.CharField(max_length=10, choices=CUSTOMER_TYPE, default='private', verbose_name='Klienta tips')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Tālrunis')

    # Uzņēmuma lauki (tikai firma)
    company_name = models.CharField(max_length=200, blank=True, verbose_name='Uzņēmuma nosaukums')
    reg_nr = models.CharField(max_length=50, blank=True, verbose_name='Reģistrācijas Nr.')
    vat_nr = models.CharField(max_length=50, blank=True, verbose_name='PVN reģ. Nr.')

    # Juridiskā adrese
    legal_address = models.CharField(max_length=300, blank=True, verbose_name='Juridiskā adrese')
    legal_city = models.CharField(max_length=100, blank=True, verbose_name='Pilsēta')
    legal_postal_code = models.CharField(max_length=20, blank=True, verbose_name='Pasta indekss')
    legal_country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default='LV', verbose_name='Valsts')

    # Faktiskā / piegādes adrese
    delivery_same = models.BooleanField(default=True, verbose_name='Faktiskā adrese = juridiskajai')
    delivery_address = models.CharField(max_length=300, blank=True, verbose_name='Faktiskā adrese')
    delivery_city = models.CharField(max_length=100, blank=True, verbose_name='Pilsēta (faktiskā)')
    delivery_postal_code = models.CharField(max_length=20, blank=True, verbose_name='Pasta indekss (faktiskā)')
    delivery_country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default='LV', blank=True, verbose_name='Valsts (faktiskā)')

    newsletter = models.BooleanField(default=True, verbose_name='Saņemt jaunumus')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lietotāja profils'
        verbose_name_plural = 'Lietotāju profili'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username}'

    def is_company(self):
        return self.customer_type == 'company'

    def get_delivery_address(self):
        if self.delivery_same:
            return {
                'address': self.legal_address,
                'city': self.legal_city,
                'postal_code': self.legal_postal_code,
                'country': self.legal_country,
            }
        return {
            'address': self.delivery_address,
            'city': self.delivery_city,
            'postal_code': self.delivery_postal_code,
            'country': self.delivery_country,
        }

    def display_name(self):
        if self.customer_type == 'company' and self.company_name:
            return self.company_name
        return self.user.get_full_name() or self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance, defaults={
            'phone': '', 'legal_address': '', 'legal_city': '', 'legal_postal_code': ''
        })
