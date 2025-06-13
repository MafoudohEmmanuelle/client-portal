from django.contrib import admin
from .models import User,Client,Commercial,LeadRequest,BE,ChefCommercial
from accounts.views import send_activation_email
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.forms import CustomUserCreationForm
from django.contrib.auth.models import User as DjangoDefaultUser

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Commercial)
admin.site.register(LeadRequest)
admin.site.register(BE)
admin.site.register(ChefCommercial)

User = get_user_model()
# Unregister default User if already registered
try:
    admin.site.unregister(DjangoDefaultUser)
except admin.sites.NotRegistered:
    pass
# Unregister your custom user if previously registered
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    model = User
    list_display = ('username', 'email', 'role', 'is_active')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.is_active = False
            obj.save()
            send_activation_email(obj,request)
        else:
            super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)