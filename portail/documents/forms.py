from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['type_documents', 'fichier']
        labels = {
            'type_documents': "Type de document",
            'fichier': "Fichier à uploader",
        }
        widgets = {
            'type_documents': forms.Select(attrs={'class': 'form-select'}),
            'fichier': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }