from django.urls import path
from .views import ouvrir_devis,upload_document,mes_documents,be_documents,cmc_documents,commercial_documents

urlpatterns = [
    path('ouvrir-devis/<int:doc_id>/', ouvrir_devis, name='ouvrir_devis'),
    path('televerser-document/<int:commande_id>/',upload_document, name='upload_document'),
    path('documents/', mes_documents, name='mes_documents'),
    path('documents/be/', be_documents, name='be_documents'),
    path('documents/commercial/', commercial_documents, name='commercial_documents'),
    path('documents/cmc/', cmc_documents, name='cmc_documents'),
]
