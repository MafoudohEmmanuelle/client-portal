from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.TextChoices):
    CLIENT = 'client', 'Client'
    COMMERCIAL = 'commercial', 'Commercial'
    BE = 'be', 'BE'
    CHEF_COMMERCIAL = 'chef_commercial', 'Chef Commercial'
    ADMIN = 'admin', 'Admin'


class User(AbstractUser):
    role = models.CharField(choices=Role.choices, max_length=20, default=Role.CLIENT)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def profile(self):
        if self.role == Role.CLIENT:
            return getattr(self, 'client_profile', None)
        elif self.role == Role.COMMERCIAL:
            return getattr(self, 'commercial_profile', None)
        elif self.role == Role.BE:
            return getattr(self, 'be_profile', None)
        elif self.role == Role.CHEF_COMMERCIAL:
            return getattr(self, 'chefcommercial_profile', None)
        return None


class Commercial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='commercial_profile')
    nom_commercial = models.CharField(max_length=50, null=True, blank=True)
    contact = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom_commercial or self.user.get_full_name() or "Commercial sans nom"

class Client(models.Model):
    CLIENT_TYPE_CHOICES = [
        ('local', 'Client Local'),
        ('international', 'Client International'),
    ]

    SECTEUR_CHOICES = [
        ('pharma', 'Pharmaceutique'),
        ('agro', 'Agroalimentaire'),
        ('cosmetique', 'Cosmétique'),
        ('chimie', 'Chimie'),
        ('autre', 'Autre'),
    ]

    ORIGINE_CHOICES = [
        ('salon', 'Salon professionnel'),
        ('site_web', 'Site Web'),
        ('recommandation', 'Recommandation'),
        ('prospection', 'Prospection'),
        ('autre', 'Autre'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    nom_entreprise = models.CharField(max_length=50)
    interlocuteur = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    ville = models.CharField(max_length=50)
    rue = models.CharField(max_length=50, null=True, blank=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    bp = models.CharField(max_length=10)
    type_client = models.CharField(choices=CLIENT_TYPE_CHOICES, max_length=20, default='local')
    commercial = models.ForeignKey(
        Commercial,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='clients'
    )
    secteur_activite = models.CharField(max_length=50, choices=SECTEUR_CHOICES, null=True, blank=True)
    origine_client = models.CharField(max_length=50, choices=ORIGINE_CHOICES, null=True, blank=True)
    date_validation_compte = models.DateField(null=True, blank=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.nom_entreprise} ({self.interlocuteur})"

class LeadRequest(models.Model):
    SECTEUR_CHOICES = [
        ('pharma', 'Pharmaceutique'),
        ('agro', 'Agroalimentaire'),
        ('cosmetique', 'Cosmétique'),
        ('chimie', 'Chimie'),
        ('autre', 'Autre'),
    ]

    ORIGINE_CHOICES = [
        ('salon', 'Salon professionnel'),
        ('site_web', 'Site Web'),
        ('recommandation', 'Recommandation'),
        ('prospection', 'Prospection'),
        ('autre', 'Autre'),
    ]

    raison_sociale = models.CharField(max_length=100)
    interlocuteur = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=15, null=True, blank=True)
    pays = models.CharField(max_length=100)
    ville = models.CharField(max_length=50)
    rue = models.CharField(max_length=50, null=True, blank=True)
    bp = models.CharField(max_length=10, null=True)
    secteur_activite = models.CharField(max_length=50, choices=SECTEUR_CHOICES, null=True, blank=True)
    origine_client = models.CharField(max_length=50, choices=ORIGINE_CHOICES, null=True, blank=True)
    source_creation=models.CharField(max_length=50, null=True)
    date_reception = models.DateTimeField(auto_now_add=True)
    valide= models.BooleanField(default=True)
    converted= models.BooleanField(default=False)

    def __str__(self):
        return f"{self.raison_sociale} ({self.interlocuteur})"


class BE(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='be_profile')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bureau d'Étude - {self.user.get_full_name()}"


class ChefCommercial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chefcommercial_profile')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chef Commercial - {self.user.get_full_name()}"
