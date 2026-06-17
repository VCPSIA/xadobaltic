from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, CUSTOMER_TYPE, COUNTRY_CHOICES


class RegisterForm(forms.Form):
    # --- Klienta tips ---
    customer_type = forms.ChoiceField(
        choices=CUSTOMER_TYPE,
        widget=forms.RadioSelect,
        initial='private',
        label='Klienta tips',
    )

    # --- Personīgie dati ---
    first_name = forms.CharField(max_length=100, label='Vārds')
    last_name = forms.CharField(max_length=100, label='Uzvārds')
    email = forms.EmailField(label='E-pasts')
    email_confirm = forms.EmailField(label='Apstiprināt e-pastu')
    phone = forms.CharField(
        max_length=30,
        label='Tālrunis',
        help_text='Piemēram: +371 20 000 000',
    )

    # --- Uzņēmuma lauki (obligāti firmām) ---
    company_name = forms.CharField(max_length=200, required=False, label='Uzņēmuma nosaukums')
    reg_nr = forms.CharField(max_length=50, required=False, label='Reģistrācijas Nr.')
    vat_nr = forms.CharField(max_length=50, required=False, label='PVN reģ. Nr. (ja ir)')

    # --- Juridiskā adrese ---
    legal_address = forms.CharField(max_length=300, label='Juridiskā adrese (iela, māja)')
    legal_city = forms.CharField(max_length=100, label='Pilsēta / novads')
    legal_postal_code = forms.CharField(max_length=20, label='Pasta indekss')
    legal_country = forms.ChoiceField(choices=COUNTRY_CHOICES, initial='LV', label='Valsts')

    # --- Faktiskā / piegādes adrese ---
    delivery_same = forms.BooleanField(
        required=False,
        initial=True,
        label='Faktiskā adrese sakrīt ar juridisko',
        widget=forms.CheckboxInput(attrs={'id': 'deliverySameCheck'}),
    )
    delivery_address = forms.CharField(max_length=300, required=False, label='Faktiskā adrese (iela, māja)')
    delivery_city = forms.CharField(max_length=100, required=False, label='Pilsēta / novads')
    delivery_postal_code = forms.CharField(max_length=20, required=False, label='Pasta indekss')
    delivery_country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False, initial='LV', label='Valsts')

    # --- Parole ---
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label='Parole',
        help_text='Vismaz 8 simboli.',
        min_length=8,
    )
    password2 = forms.CharField(widget=forms.PasswordInput, label='Apstiprināt paroli')

    newsletter = forms.BooleanField(required=False, initial=True, label='Vēlos saņemt jaunumus un piedāvājumus')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Šāds e-pasts jau ir reģistrēts.')
        return email

    def clean(self):
        cleaned = super().clean()

        # E-pasta apstiprinājums
        email = cleaned.get('email', '').lower()
        email_confirm = cleaned.get('email_confirm', '').lower()
        if email and email_confirm and email != email_confirm:
            self.add_error('email_confirm', 'E-pasta adreses nesakrīt.')

        # Paroles apstiprinājums
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Paroles nesakrīt.')

        # Uzņēmuma obligātie lauki
        if cleaned.get('customer_type') == 'company':
            if not cleaned.get('company_name'):
                self.add_error('company_name', 'Obligāts lauks uzņēmumiem.')
            if not cleaned.get('reg_nr'):
                self.add_error('reg_nr', 'Obligāts lauks uzņēmumiem.')

        # Faktiskā adrese (ja nav atzīmēta "sakrīt")
        if not cleaned.get('delivery_same'):
            if not cleaned.get('delivery_address'):
                self.add_error('delivery_address', 'Ievadiet faktisko adresi.')
            if not cleaned.get('delivery_city'):
                self.add_error('delivery_city', 'Ievadiet pilsētu.')
            if not cleaned.get('delivery_postal_code'):
                self.add_error('delivery_postal_code', 'Ievadiet pasta indeksu.')

        return cleaned

    def save(self):
        data = self.cleaned_data
        # Izveido lietotāju
        username = data['email'].split('@')[0].lower()
        base = username
        n = 1
        while User.objects.filter(username=username).exists():
            username = f'{base}{n}'
            n += 1
        user = User.objects.create_user(
            username=username,
            email=data['email'].lower(),
            password=data['password1'],
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
        # Izveido profilu
        profile = user.profile
        profile.customer_type = data['customer_type']
        profile.phone = data['phone']
        profile.company_name = data.get('company_name', '')
        profile.reg_nr = data.get('reg_nr', '')
        profile.vat_nr = data.get('vat_nr', '')
        profile.legal_address = data['legal_address']
        profile.legal_city = data['legal_city']
        profile.legal_postal_code = data['legal_postal_code']
        profile.legal_country = data['legal_country']
        profile.delivery_same = data.get('delivery_same', True)
        profile.delivery_address = data.get('delivery_address', '')
        profile.delivery_city = data.get('delivery_city', '')
        profile.delivery_postal_code = data.get('delivery_postal_code', '')
        profile.delivery_country = data.get('delivery_country', 'LV')
        profile.newsletter = data.get('newsletter', False)
        profile.save()
        return user


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label='Vārds')
    last_name = forms.CharField(max_length=100, required=False, label='Uzvārds')
    email = forms.EmailField(required=True, label='E-pasts')

    class Meta:
        model = UserProfile
        fields = (
            'customer_type', 'phone',
            'company_name', 'reg_nr', 'vat_nr',
            'legal_address', 'legal_city', 'legal_postal_code', 'legal_country',
            'delivery_same',
            'delivery_address', 'delivery_city', 'delivery_postal_code', 'delivery_country',
            'newsletter',
        )
        widgets = {
            'customer_type': forms.RadioSelect,
            'delivery_same': forms.CheckboxInput(attrs={'id': 'deliverySameCheck'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.RadioSelect, forms.CheckboxInput)):
                field.widget.attrs.setdefault('class', 'form-control')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('customer_type') == 'company':
            if not cleaned.get('company_name'):
                self.add_error('company_name', 'Obligāts lauks uzņēmumiem.')
            if not cleaned.get('reg_nr'):
                self.add_error('reg_nr', 'Obligāts lauks uzņēmumiem.')
        if not cleaned.get('delivery_same'):
            for f in ('delivery_address', 'delivery_city', 'delivery_postal_code'):
                if not cleaned.get(f):
                    self.add_error(f, 'Obligāts lauks.')
        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            self.user.save()
        if commit:
            profile.save()
        return profile
