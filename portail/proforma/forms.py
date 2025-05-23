from django import forms
from .models import Proforma, ProformaItem
from django.forms import inlineformset_factory
from decimal import Decimal

class ProformaNouveauProduitForm(forms.ModelForm):
    prix_unitaire = forms.DecimalField(label="Prix unitaire", max_digits=10, decimal_places=2,widget=forms.NumberInput(attrs={'class': 'form-control'}))
    modalites_reglement = forms.CharField(label="Modalités de règlement", widget=forms.Textarea(attrs={'class': 'form-control', 'row': 1 }))
    condition_ht = forms.CharField(label="Conditions HT", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'row': 1 }))

    class Meta:
        model = Proforma
        fields = ['modalites_reglement', 'condition_ht']


class ProformaForm(forms.ModelForm):
    class Meta:
        model = Proforma
        fields = ['modalites_reglement', 'condition_ht']

ProformaItemFormSet = inlineformset_factory(
    Proforma,
    ProformaItem,
    fields=['produit', 'designation', 'quantite', 'unite', 'prix_unitaire'],
    extra=0,
    can_delete=False
)

class RefusCommentaireForm(forms.Form):
    commentaire_refus = forms.CharField(
        label="Pourquoi refusez-vous cette proforma ?",
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=True
    )

class ProformaOldProduitForm(forms.Form):
    modalites_reglement = forms.CharField(
        label="Modalités de règlement",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        required=True
    )
    condition_ht = forms.CharField(
        label="Conditions HT (optionnel)",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        items = kwargs.pop('items', [])
        super().__init__(*args, **kwargs)

        for item in items:
            field_name = f"prix_{item.id}"
            self.fields[field_name] = forms.DecimalField(
                label=f"Prix unitaire pour {item.produit.designation}",
                min_value=Decimal("0.00"),
                decimal_places=2,
                max_digits=10,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
            )
