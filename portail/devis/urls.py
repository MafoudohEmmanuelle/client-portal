from django.urls import path
from .views import DevisWizard
from . import views

urlpatterns = [
    path('demande-devis/', DevisWizard.as_view(), name='demande_devis'),
    path('devis/',views.devis_par_client, name='devis_par_client'),
    path('devis/traiter/<int:devis_id>/', views.traiter_devis, name='traiter_devis'),
    path('devis/modifier/<int:devis_id>/', views.modifier_devis, name='modifier_devis'),
    path('devis/BE/traiter/<int:devis_id>/', views.traiter_devis_be, name='traiter_devis_be'),
    path('devis/complet',views.devis_complet, name='devis_complet'),
    path('devis/detail/<int:devis_id>/', views.detail_devis, name='detail_devis'),
]
