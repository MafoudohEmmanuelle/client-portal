from django.db import models
from accounts.models import Client
from devis.models import Categorie, DevisNouveauProduit

class Produit(models.Model):
    designation = models.CharField(max_length=100)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True)
    unite = models.CharField(max_length=20, choices=[('kg', 'Kg'), ('pièce', 'Pièce')], null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    proforma_origine = models.ForeignKey('Proforma', on_delete=models.SET_NULL, null=True, blank=True)
    
class Proforma(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    quote = models.ForeignKey('ProduitQuote', on_delete=models.CASCADE, null=True, blank=True, related_name="proformas")
    devis = models.ForeignKey(DevisNouveauProduit, on_delete=models.CASCADE, null=True, blank=True, related_name="proformas")
    modalites_reglement = models.TextField()
    condition_ht = models.TextField(blank=True, null=True)
    montant_total_ht = models.DecimalField(max_digits=12, decimal_places=2)
    tva = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    net_a_payer = models.DecimalField(max_digits=12, decimal_places=2)
    net_a_payer_lettres = models.CharField(max_length=255, blank=True)
    commentaire_refus_cmc = models.TextField(blank=True)
    commentaire_refus_client = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('valide','Validée par le CMC'),
        ('non_valide','Non Validée par le CMC')
    ], default='en_attente')
    date_envoie = models.DateTimeField(auto_now_add=True)
    generated_doc=models.OneToOneField('documents.GeneratedDoc',on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Proforma #{self.id} - {self.client.nom_entreprise}"

class ProformaItem(models.Model):
    proforma = models.ForeignKey(Proforma, on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, null=True, blank=True)
    designation = models.CharField(max_length=100)
    quantite = models.PositiveIntegerField()
    unite = models.CharField(max_length=20, choices=[('kg', 'Kg'), ('pièce', 'Pièce')])
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    montant = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.designation} (x{self.quantite})"

# --- For old product selection ---

class ProduitQuote(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[
        ('nouveau', 'Nouveau'),
        ('en_traitement', 'En traitement'),
        ('proforma_envoyee', 'Proforma envoyée'),
    ], default='en_attente')
    
class ProduitQuoteItem(models.Model):
    quote = models.ForeignKey(ProduitQuote, on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    unite = models.CharField(max_length=20, choices=[('kg', 'Kg'), ('pièce', 'Pièce')], null=True)
    

class CoordonneeBancaire(models.Model):
    banque = models.CharField(max_length=50)
    code_banque = models.CharField(max_length=6)
    code_guichet = models.CharField(max_length=6)
    num_compte = models.CharField(max_length=20)
    cle = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.banque} - {self.num_compte}"
