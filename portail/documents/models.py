from django.db import models
from accounts.models import User,Client
from orders.models import Commande

class Document(models.Model):
    choix_document = [
        ('bon_commande', 'Bon de Commande'),
        ('proforma','Proforma'),
        ('facture', 'Facture'),
        ('devis', 'Fiche de Devis'),
    ]
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='documents')
    client= models.ForeignKey(Client,on_delete=models.SET_NULL, null=True)
    uploaded_by= models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    type_documents = models.CharField(max_length=50, choices=choix_document)
    fichier = models.FileField(upload_to='documents/')
    date_upload= models.DateField()

    def __str__(self):
        return f"{self.get_type_documents_display()} - {self.id_document}"

class GeneratedDoc(models.Model):
    choix_document = [
        ('proforma','Proforma'),
        ('devis', 'Fiche de Devis'),
    ]
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    doc = models.FileField(upload_to='generated_docs/')
    type_doc = models.CharField(max_length=50, choices=choix_document)
    date_creation = models.DateTimeField(auto_now_add=True)
    commande = models.ForeignKey(Commande, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return f"{self.type_doc} - {self.generated_by} - {self.date_creation.strftime('%Y-%m-%d')}"
