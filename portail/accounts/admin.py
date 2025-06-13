from django.contrib import admin
from .models import User,Client,Commercial,LeadRequest,BE,ChefCommercial
from accounts.views import send_activation_email

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Commercial)
admin.site.register(LeadRequest)
admin.site.register(BE)
admin.site.register(ChefCommercial)

class UserAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.is_active = False  # User inactive until activation
            obj.save()

            # Call the activation email function
            send_activation_email(request, obj)
        else:
            super().save_model(request, obj, form, change)

admin.site.register(User, UserAdmin)
