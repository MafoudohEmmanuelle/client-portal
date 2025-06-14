from django.contrib import admin
from .models import User,Client,Commercial,LeadRequest,BE,ChefCommercial
from accounts.views import send_activation_email
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm

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
def save_model(request, obj, form, change):
    if not change: 
        obj.is_active = False
    super().save_model(request, obj, form, change)
    if not change:
        send_activation_email(obj, request)

admin.site.register(User, UserAdmin)