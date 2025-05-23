from django import forms
from .models import DevisNouveauProduit,Categorie,FinitionConditionnement,Support, AnalyseTechniqueBE,Coloration,Outillage,Cotation
from django.forms import modelformset_factory

class DevisForm(forms.ModelForm):
    bool_choices = [(True, 'Oui'), (False, 'Non')]

    famille_produit = forms.ModelChoiceField(
        queryset=Categorie.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
    )

    fiche_technique = forms.ChoiceField(
        choices=bool_choices,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
    )

    echantillon_disponible = forms.ChoiceField(
        choices=bool_choices,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
    )

    visuel_disponible = forms.ChoiceField(
        choices=bool_choices,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
    )

    devis_identique = forms.ChoiceField(
        choices=bool_choices,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
    )

    accessoires_payants = forms.ChoiceField(
        choices=bool_choices,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
        label="Accessoires payants",
    )

    class Meta:
        model = DevisNouveauProduit
        fields = [
            'designation_produit',
            'famille_produit',
            'quantite_previsionnelle',
            'unite',
            'periode',
            'fiche_technique',
            'echantillon_disponible',
            'visuel_disponible',
            'devis_identique',
            'accessoires_payants',
            'longueur_produit',
            'largeur_produit',
        ]
        widgets = {
            'designation_produit': forms.TextInput(attrs={'class': 'form-control'}),
            'quantite_previsionnelle': forms.NumberInput(attrs={'class': 'form-control'}),
            'unite': forms.Select(attrs={'class': 'form-select'}),
            'periode': forms.Select(attrs={'class': 'form-select'}),
            'largeur_produit': forms.NumberInput(attrs={'class': 'form-control'}),
            'longueur_produit': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'designation_produit': 'Désignation du produit',
            'quantite_previsionnelle': 'Quantité prévisionnelle consommable',
            'unite': 'Unité de mesure',
            'periode': 'Fréquence prévisionnelle de consommation',
            'largeur_produit': 'Largeur (mm)',
            'longueur_produit': 'Longueur (mm)',
        }

class FinitionConditionnementForm(forms.ModelForm):
    class Meta:
        
        BOOL_CHOICES = [('True', 'Oui'), ('False', 'Non')]

        autocolant_utilise = forms.ChoiceField(
            choices=BOOL_CHOICES,
            widget=forms.RadioSelect(attrs={'class': 'form-check-input livraison-bobine','id': 'id_autocollant'}),
            required=True,
        )
        model = FinitionConditionnement
        fields = [
            'mode_utilisation',
            'mode_livraison',
            'sens_deroulement',
            'nature_mandrin',
            'diametre_mandrin',
            'epaisseur_mandrin',
            'poids_max_bobine',
            'diametre_bobine',
            'nb_bobines_par_palette',
            'autocolant_utilise',
            'espace_pose_min',
            'espace_pose_max',
            'contenant',
            'conditionnement',
            'nb_pieces',
        ]
        labels = {
            'mode_utilisation': 'Mode d\'utilisation',
            'mode_livraison': 'Mode de livraison',
            'sens_deroulement': 'Sens de déroulement',
            'nature_mandrin': 'Nature du mandrin',
            'diametre_mandrin': 'Diamètre du mandrin',
            'epaisseur_mandrin': 'Épaisseur du mandrin',
            'poids_max_bobine': 'Poids de la bobine',
            'diametre_bobine': 'Diamètre max de la bobine',
            'nb_bobines_par_palette': 'Nombre de bobines par palette',
            'autocolant_utilise': 'Nécessité d\'autocollant lors de l\'utilisation',
            'espace_pose_min': 'Espacement de pose minimum (mm)',
            'espace_pose_max': 'Espacement de pose maximum (mm)',
            'contenant': 'Contenant du produit à la livraison',
            'conditionnement': 'Conditionnement(Emballage) du produit a la livraison',
            'nb_pieces':'Nombre de pièces',
        }
        widgets = { 
            'mode_utilisation': forms.Select(attrs={'class': 'form-select'}),
            'mode_livraison': forms.Select(attrs={'class': 'form-select', 'id': 'id_mode_livraison'}),
            'sens_deroulement': forms.Select(attrs={'class': 'form-select livraison-bobine', 'name':'deroulement'}),
            'nature_mandrin': forms.Select(attrs={'class': 'form-select livraison-bobine'}),
            'diametre_mandrin': forms.Select(attrs={'class': 'form-select livraison-bobine'}),
            'epaisseur_mandrin': forms.NumberInput(attrs={'class': 'form-control livraison-bobine', 'placeholder': 'Ex: 1.5mm', 'step': 0.1}),
            'poids_max_bobine': forms.NumberInput(attrs={'class': 'form-control livraison-bobine', 'placeholder': 'Ex: 2.5kg', 'step': 0.1}),
            'diametre_bobine': forms.NumberInput(attrs={'class': 'form-select livraison-bobine', 'step': 0.01}),
            'nb_bobines_par_palette':forms.NumberInput(attrs={'class': 'form-control livraison-bobine'}),
            'espace_pose_min':  forms.NumberInput(attrs={'class': 'form-control autocollant-oui ', 'step': 0.01}),
            'espace_pose_max': forms.NumberInput(attrs={'class': 'form-control  autocollant-oui ', 'step': 0.01}),
            'contenant': forms.Select(attrs={'class': 'form-select'}),
            'conditionnement': forms.Select(attrs={'class': 'form-select'}),
            'nb_pieces': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SupportForm(forms.ModelForm):
    class Meta:
        model = Support
        fields = ['type_support', 'couleur', 'epaisseur', 'grammage']
        widgets = {
            'type_support': forms.TextInput(attrs={'class': 'form-control'}),
            'couleur': forms.TextInput(attrs={'class': 'form-control'}),
            'epaisseur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'grammage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        if all(not cleaned_data.get(field) for field in self.fields):
            self.empty_permitted = True  
        return cleaned_data
    
SupportFormSet = modelformset_factory(
    Support,
    form=SupportForm,
    extra=1, 
    can_delete=True,
)

class BEDevisForm(forms.ModelForm):
    class Meta:
        model=AnalyseTechniqueBE
        fields=[
        'format_support_longueur',
        'format_support_largeur',
        'type_impression',
        'sens_impression',
        'type_encre', 
        'dorure',
        'colle_complexage',
        'plastification',
        'decoupe',
        ]
        labels={
            'format_support_longueur':'Longueur du support',
            'format_support_largeur':'Largeur du support',
            'type_impression': 'Type d\'impression',
            'sens_impression':'Sens d\'impression',
            'type_encre':'Type d\'encre', 
            'dorure':'Dorure',
            'colle_complexage':'Colle complexage',
            'plastification':'Plastification',
            'decoupe': 'Découpe',
        }
        widgets={
            'format_support_longueur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'format_support_largeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'type_impression': forms.TextInput(attrs={'class': 'form-control'}),
            'sens_impression': forms.TextInput(attrs={'class': 'form-control'}),
            'type_encre': forms.TextInput(attrs={'class': 'form-control'}), 
            'dorure': forms.TextInput(attrs={'class': 'form-control'}),
            'colle_complexage': forms.TextInput(attrs={'class': 'form-control'}),
            'plastification': forms.TextInput(attrs={'class': 'form-control'}),
            'decoupe': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ColourForm(forms.ModelForm):
    class Meta:
       model= Coloration
       fields=['couleur']
       widgets={
          'couleur': forms.TextInput(attrs={'class': 'form-control'}),
       }
       labels={'couleur': 'Couleur ou venis'}

class OutillageForm(forms.ModelForm):
    class Meta:
        model = Outillage
        fields = ['type_outillage', 'quantite', 'prix_unitaire']
        widgets = {
            'type_outillage': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels={
            'type_outillage': 'Outillage',
            'quantite': 'Quantité',
            'prix_unitaire': 'Prix unitaire',
       }

class CotationForm(forms.ModelForm):
    class Meta:
        model = Cotation
        fields = ['cotation_unitaire', 'quantite', 'taux_mat']
        widgets = {
            'cotation_unitaire': forms.NumberInput(attrs={'class': 'form-control','step': '0.01'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'taux_mat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels={
            'type_outillage': 'Cotation Unitaire(fcfa)',
            'quantite': 'Quantité',
            'prix_unitaire': 'Taux matière première',
       }

ColorationFormSet = modelformset_factory(Coloration, form=ColourForm, extra=1, can_delete=True)
OutillageFormSet = modelformset_factory(Outillage, form=OutillageForm, extra=1, can_delete=True)
CotationFormSet = modelformset_factory(Cotation,form=CotationForm, extra=1, can_delete=True)
