from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('accounts.urls')),
    path('',include('dashboard.urls')),
    path('',include('devis.urls')),
    path('',include('documents.urls')),
    path('',include('proforma.urls')),
    path('',include('orders.urls')),
]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
