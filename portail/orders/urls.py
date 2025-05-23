from django.urls import path
from . import views

urlpatterns = [
    path('proforma/<int:proforma_id>/commande',views.passer_commande_depuis_proforma, name='passer_commande_depuis_proforma'),
    path('mes-commandes/', views.commandes_client, name='commandes_client'),
    path('commande/<int:commande_id>/', views.commande_detail, name='commande_detail'),
    path('mes-commandes/<int:id_commande>/', views.commande_detail_client, name='commande_detail_client'),
    path('commandes/<int:commande_id>', views.valider_commande_view, name='valider_commande'),
    path('commandes/', views.liste_commandes, name='liste_commandes'),
]