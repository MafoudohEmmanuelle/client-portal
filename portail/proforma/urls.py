from django.urls import path
from . import views

urlpatterns = [
    path('proforma/creer/<int:devis_id>/', views.creer_proforma_nouveau_produit, name='creer_proforma'),
    path('proforma/creer/old/<int:quote_id>/', views.creer_proforma_old, name='creer_proforma_old'),
    path('proforma/visualiser/<int:proforma_id>/', views.visualiser_proforma, name='visualiser_proforma'),
    path('proforma/envoyer/<int:proforma_id>/', views.envoyer_proforma, name='envoyer_proforma'),
    path('offre/liste/<int:devis_id>/',views.proforma_devis, name='proforma_devis'),
    path('quote_offer/liste/<int:quote_id>/',views.proforma_quote, name='proforma_quote'),
    path('proforma/liste/', views.list_proforma, name='list_proforma'),
    path('proforma/cmc/accepter/<int:proforma_id>/', views.valider_proforma_cmc, name='valider_proforma_cmc'),
    path('proforma/cmc/refuser/<int:proforma_id>/', views.refuser_proforma_cmc, name='refuser_proforma_cmc'),
    path('client/offres/', views.offres_client, name='offres_client'),
    path('client/offre/<int:proforma_id>/accepter/', views.accepter_offre, name='accepter_offre'),
    path('client/offre/<int:proforma_id>/refuser/', views.refuser_offre, name='refuser_offre'),
    path('offres/detail/<int:proforma_id>/', views.detail_proforma_client, name='detail_proforma_client'),
    path('proforma_acceptee/', views.proformas_acceptees, name='proformas_acceptees'),
    path('catalogue/', views.produits_client, name='produits_client'),
    path('add-to-quote/<int:produit_id>/', views.add_to_quote, name='add_to_quote'),
    path('quote/', views.quote_view, name='quote_view'),
    path('quote/remove/<int:item_id>/', views.remove_from_quote, name='remove_from_quote'),
    path('cancel-quote/', views.cancel_quote, name='cancel_quote'),
    path('quote/submit/', views.submit_quote, name='submit_quote'),
    path('cotations/', views.liste_quotes, name='liste_quotes'),
    path('cotations/detail/<int:quote_id>/', views.detail_quote, name='detail_quote'),
    path('liste-devis-cotation/', views.liste_devis_et_quotes, name='liste_devis_et_quotes')
]
