from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('login/',views.user_login,name='login'),
    path('client/register/',views.register_client, name='client_registration'),
    path('commercial/register/', views.register_commercial, name='commercial_register'),
    path('lead/register/',views.lead_request, name='lead_request'),
    path('mon-profil/', views.profile_view, name='profile_view'),
    path('mes_client/',views.liste_clients, name='liste_client'),
    path('client/', views.liste_clients_cmc,name='liste_client_cmc'),
    path('commercial/', views.liste_commercial, name='liste_commercial'),
    path('lead/',views.liste_lead, name='liste_lead'),
    path('logout/',views.logout_user,name='logout'),
    path('client/register/cmc/',views.register_client_cmc, name='register_client_cmc'),
    path('lead/validation/<int:lead_id>/', views.lead_validation, name='lead_validation'),
    path('lead/<int:lead_id>/refuser/', views.refuser_lead, name='refuser_lead'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='set_password'),
]