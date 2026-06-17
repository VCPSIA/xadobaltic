from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fieldsets = (
        ('Tips un kontakti', {'fields': ('customer_type', 'phone', 'newsletter')}),
        ('Uzņēmums', {'fields': ('company_name', 'reg_nr', 'vat_nr')}),
        ('Juridiskā adrese', {'fields': ('legal_address', 'legal_city', 'legal_postal_code', 'legal_country')}),
        ('Faktiskā adrese', {'fields': ('delivery_same', 'delivery_address', 'delivery_city', 'delivery_postal_code', 'delivery_country')}),
    )


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_customer_type', 'get_phone', 'is_active', 'date_joined')
    inlines = [UserProfileInline]

    def get_customer_type(self, obj):
        p = getattr(obj, 'profile', None)
        return p.get_customer_type_display() if p else '—'
    get_customer_type.short_description = 'Tips'

    def get_phone(self, obj):
        p = getattr(obj, 'profile', None)
        return p.phone if p else '—'
    get_phone.short_description = 'Tālrunis'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
