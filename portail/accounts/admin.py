from django.contrib import admin
from .models import User,Client,Commercial,LeadRequest,BE,ChefCommercial
from accounts.views import send_activation_email
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages

admin.site.register(Client)
admin.site.register(Commercial)
admin.site.register(LeadRequest)
admin.site.register(BE)
admin.site.register(ChefCommercial)

class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')

    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'is_active')}
        ),
    )
def save_model(self, request, obj, form, change):
    if not change:
        obj.is_active = False
    super().save_model(request, obj, form, change)
    if not change:
        try:
            send_activation_email(obj, request)
            self.message_user(request, "Le mail d'activation a été envoyé avec succès.", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Erreur lors de l'envoi du mail : {e}", level=messages.ERROR)

admin.site.register(User, UserAdmin)