from django.contrib import admin
from .models import Document,GeneratedDoc

admin.site.register(Document)
admin.site.register(GeneratedDoc)