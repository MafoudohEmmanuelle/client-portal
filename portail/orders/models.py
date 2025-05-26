from django.db import models
from accounts.models import Client
from proforma.models import Proforma  # Si les commandes viennent suite à une proforma
    
class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepted', 'Acceptée'),
        ('delivered', 'Livrée'),
        ('rejected', 'Refusée'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commandes')
    proforma = models.ForeignKey(Proforma, on_delete=models.CASCADE, limit_choices_to={'statut': 'acceptee'}, null=True)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    date_livraison = models.DateField()
    requiert_certificat_analyse = models.BooleanField(default=False)
    requiert_attestation = models.BooleanField(default=False)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.client.nom_entreprise}"
