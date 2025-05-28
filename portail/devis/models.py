from django.db import models
from accounts.models import Client

class Categorie(models.Model):
    nom_categorie = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.nom_categorie}"

class FinitionConditionnement(models.Model):
    choix_utilisation = [
        ('utilisation automatique', 'Utilisation Automatique'),
        ('utilisation manuelle', 'Utilisation Manuelle'),
    ]
    choix_livraison = [
        ('bobine', 'Bobine'),
        ('sachet','Sachet'),
        ('piece_format','Piece au format'),
        ('planche','Planche'),
        ('au_choix', 'Au choix'),
    ]
    choix_mandrin = [
        ('carton', 'Carton'),
        ('pvc', 'PVC'),
    ]
    choix_diametre = [
        ('40mm', '40 mm'),
        ('76mm', '76 mm'),
        ('152mm', '152 mm'),
        ('autres', 'Autres'),
    ]
    choix_deroulement=[
        ('A1','A/1'),
        ('B1','B/1'),
        ('C1','C/1'),
        ('D1','D/1'),
        ('A2','A/2'),
        ('B2','B/2'),
        ('C2','C/2'),
        ('D2','D/2'),
    ]
    choix_emballage=[
        ('film_etirable','Film Etirable'),
        ('film_pe','Film PE'),
        ('carton','Carton'),
        ('film_pe_carton','Film PE et Carton'),
        ('film_etirable_carton','Film Etirable et Carton'),
        ('autres','Autres'),
    ]
    choix_contenance=[
        ('carton','Carton'),
        ('pile','Pile'),
        ('paquet','Paquet'),
    ]
    mode_utilisation = models.TextField(choices=choix_utilisation)
    mode_livraison = models.TextField(choices=choix_livraison)
    sens_deroulement = models.CharField(choices=choix_deroulement, max_length=100, blank=True, null=True)
    nature_mandrin = models.CharField(choices=choix_mandrin, max_length=100, blank=True, null=True)
    diametre_mandrin = models.CharField(choices=choix_diametre,blank=True, null=True,  max_length=100)
    epaisseur_mandrin = models.FloatField(blank=True, null=True)
    poids_max_bobine = models.FloatField(blank=True, null=True)
    diametre_bobine= models.FloatField(blank=True, null=True)
    nb_bobines_par_palette = models.PositiveIntegerField(blank=True, null=True)
    autocolant_utilise = models.BooleanField(default=False)
    espace_pose_min = models.FloatField(blank=True, null=True)
    espace_pose_max = models.FloatField(blank=True, null=True)
    contenant=models.CharField(choices=choix_contenance,blank=True, null=True, max_length=100, help_text="Vous n\'aurez pas forcement besoin de choisir un contenant si vous avez choisir la bobine comme mode de livraison")
    conditionnement = models.CharField(choices=choix_emballage,max_length=100)
    nb_pieces= models.PositiveIntegerField(blank=True, null=True, help_text="Donner le nombre de pièces par bobine,par carton, par parquet ou par pile dependant de ce que vous avez choisi")

class AnalyseTechniqueBE(models.Model):
    format_support_longueur = models.FloatField(blank=True, null=True)
    format_support_largeur = models.FloatField(blank=True, null=True)
    type_impression = models.CharField(max_length=100, blank=True,null=True)
    sens_impression = models.CharField(max_length=100, blank=True,null=True)
    type_encre = models.CharField(max_length=100, blank=True,null=True)
    dorure = models.CharField(max_length=100, blank=True,null=True)
    colle_complexage = models.CharField(max_length=100, blank=True,null=True)
    plastification = models.CharField(max_length=100, blank=True,null=True)
    decoupe = models.CharField(max_length=100, blank=True,null=True)
   
class Coloration(models.Model):
    analyseTech=models.ForeignKey(AnalyseTechniqueBE, on_delete=models.CASCADE, null=True, blank=True)
    couleur=models.CharField(max_length=20,null=True, blank=True)

class Outillage(models.Model):
    TYPE_OUTILLAGE_CHOICES = [
        ('cylindre', "Cylindre d'impression"),
        ('cliche', "Cliché d'impression"),
        ('plaque_decoupe', "Plaque de découpe"),
        ('plaque_dorure', "Plaque de dorure"),
        ('emporte_piece', "Emporte pièce"),
    ]
    analyse=models.ForeignKey(AnalyseTechniqueBE,on_delete=models.CASCADE, null=True)
    type_outillage = models.CharField(max_length=50, choices=TYPE_OUTILLAGE_CHOICES, null=True)
    quantite = models.PositiveIntegerField(null=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.get_type_outillage_display()} pour analyse {self.analyse.id}"
    
class Cotation(models.Model):
    analyseBe=models.ForeignKey(AnalyseTechniqueBE,on_delete=models.CASCADE, null=True)
    cotation_unitaire=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    quantite = models.PositiveIntegerField(null=True)
    taux_mat = models.DecimalField(max_digits=5, decimal_places=2, null= True)

class DevisNouveauProduit(models.Model):
    STATUS_CHOICES = [
        ('nouveau', 'Nouveau'),    
        ('en_traitement', 'En traitement'), 
        ('envoye_be', 'Nouveau Devis'),
        ('en_traitement_be','En cour de traitement'),
        ('complet', 'Devis Complet'),
        ('finalise', 'Finaliséé')
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='devis')
    designation_produit = models.CharField(max_length=255)
    famille_produit = models.ForeignKey(Categorie,on_delete=models.CASCADE)
    quantite_previsionnelle = models.IntegerField()
    unite = models.CharField(max_length=20, choices=[('kg', 'Kg'), ('pièce', 'Pièce')])
    periode = models.CharField(max_length=20, choices=[
        ('mois', 'Mois'),
        ('semaine', 'Semaine'),
        ('trimestre', 'Trimestre'),
        ('semestre', 'Semestre'),
        ('année', 'Année')
    ])
    fiche_technique = models.BooleanField(default=False)
    echantillon_disponible = models.BooleanField(default=False)
    visuel_disponible = models.BooleanField(default=False)
    devis_identique = models.BooleanField(default=False)
    accessoires_payants = models.BooleanField(default=False)
    longueur_produit = models.FloatField(help_text="en mm")
    largeur_produit = models.FloatField(help_text="en mm")
    finition_conditionnement = models.OneToOneField(FinitionConditionnement, on_delete=models.CASCADE)
    analyseBE=models.ForeignKey(AnalyseTechniqueBE, on_delete=models.CASCADE, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=30, choices=STATUS_CHOICES, default='nouveau')
    update_date= models.DateTimeField(null=True, blank=True)
    traitement_date= models.DateTimeField(null=True, blank=True)
    lu=models.BooleanField(default=False)
    generated_doc=models.OneToOneField('documents.GeneratedDoc',on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Devis #{self.id} - {self.designation_produit}"

class Support(models.Model):
    devis = models.ForeignKey('DevisNouveauProduit', on_delete=models.CASCADE, related_name='supports')
    type_support = models.CharField(max_length=100, null=True, blank=True)
    couleur = models.CharField(max_length=50, null=True, blank=True)
    epaisseur = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grammage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.type_support} - {self.couleur} ({self.epaisseur} mm, {self.grammage} g)"

