from django.contrib import admin
from .models import User,Client,Commercial,LeadRequest,BE,ChefCommercial

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Commercial)
admin.site.register(LeadRequest)
admin.site.register(BE)
admin.site.register(ChefCommercial)