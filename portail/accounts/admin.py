from django.contrib import admin
from .models import User,Client,Commercial,LeadRequest,BE,ChefCommercial
from accounts.views import send_activation_email
from django.contrib.auth import get_user_model

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Commercial)
admin.site.register(LeadRequest)
admin.site.register(BE)
admin.site.register(ChefCommercial)

User = get_user_model()
# Unregister the existing User model
admin.site.unregister(User)

class UserAdmin(BaseUserAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.is_active = False
            obj.save()
            send_activation_email(request, obj)
        else:
            super().save_model(request, obj, form, change)

# Register it again with the custom admin
admin.site.register(User, UserAdmin)

