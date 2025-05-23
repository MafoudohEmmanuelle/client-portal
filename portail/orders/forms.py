from django import forms
from .models import Commande
from documents.models import Document

class CommandeForm(forms.ModelForm):
    date_livraison = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    requiert_certificat_analyse = forms.BooleanField(required=False)
    requiert_attestation = forms.BooleanField(required=False)

    class Meta:
        model = Commande
        fields = ['date_livraison', 'requiert_certificat_analyse', 'requiert_attestation', 'prix_total']


class BonCommandeUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['fichier']
        widgets = {
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
        }
