from django import forms
from .models import PAYMENT_METHOD

COUNTRY_CHOICES = [
    ('Latvija', 'Latvija'),
    ('Lietuva', 'Lietuva'),
    ('Igaunija', 'Igaunija'),
    ('Somija', 'Somija'),
    ('Zviedrija', 'Zviedrija'),
    ('Vācija', 'Vācija'),
    ('Cita', 'Cita'),
]


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200, label='Vārds Uzvārds')
    email = forms.EmailField(label='E-pasts')
    phone = forms.CharField(max_length=30, label='Tālrunis')
    company = forms.CharField(max_length=200, required=False, label='Uzņēmums (neobligāts)')
    vat_nr = forms.CharField(max_length=50, required=False, label='PVN Nr. (neobligāts)')
    address_line1 = forms.CharField(max_length=300, label='Adrese')
    address_line2 = forms.CharField(max_length=300, required=False, label='Adrese 2 (dzīvoklis u.c.)')
    city = forms.CharField(max_length=100, label='Pilsēta')
    postal_code = forms.CharField(max_length=20, label='Pasta indekss')
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, label='Valsts')
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD, label='Maksājuma veids', widget=forms.RadioSelect)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label='Piezīmes pasūtījumam')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs['class'] = 'form-control'
