from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/client/',views.client_dashboard, name='client_dashboard'),
    path('dashboard/commercial/',views.commercial_dashboard, name='commercial_dashboard'),
    path('dashboard/cmc/',views.chef_dashboard, name='chef_dashboard'),
    path('dashboard/BE/',views.be_dashboard, name='be_dashboard'),
    path('commandes-par-mois/', views.commandes_par_mois, name='commandes_par_mois'),
    path('stats/commandes-par-client/', views.commandes_par_client, name='commandes_par_client'),
]
