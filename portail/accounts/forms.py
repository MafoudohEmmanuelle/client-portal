from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm as DjangoSetPasswordForm
from django.utils import timezone
from .models import User, Client, Commercial, BE, LeadRequest
from django_countries.widgets import CountrySelectWidget
from phonenumber_field.formfields import PhoneNumberField
from django_countries.fields import CountryField
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        user.is_active = False
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    username= forms.CharField( label="", widget=forms.TextInput(attrs={'class':'form-control form-control-lg', 'placeholder':'Entrez votre nom '}),required=True)
    password= forms.CharField( label="", widget=forms.PasswordInput(attrs={'class':'form-control form-control-lg', 'placeholder':'Entrez votre mot de passe'}),required=True)

class SetPasswordForm(DjangoSetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['new_password1'].label = "Nouveau mot de passe"
        self.fields['new_password2'].label = "Confirmer le mot de passe"

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control form-control-lg',
                'placeholder': field.label
            })

class LeadRegistrationForm(forms.ModelForm):
    pays = CountryField().formfield(
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Pays"
    )
    telephone= PhoneNumberField(label="Numéro de téléphone", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ex: +237 6xx xxx xxx'
    }))
    class Meta:
        model = LeadRequest
        fields = [
            'raison_sociale', 'interlocuteur', 'email', 'telephone',
            'pays', 'ville', 'rue', 'bp',
            'secteur_activite', 'origine_client'
        ]
        widgets = {
            'raison_sociale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom de l'entreprise"}),
            'interlocuteur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom du contact"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Adresse email"}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ville"}),
            'rue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Rue"}),
            'bp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Boîte postale"}),
            'secteur_activite': forms.Select(attrs={'class': 'form-control'}),
            'origine_client': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        lead = super().save(commit=False)
        lead.source_creation = "formulaire_site"
        lead.date_reception = timezone.now()
        if commit:
            lead.save()
        return lead

class ClientRegistrationForm(forms.ModelForm):
    pays = CountryField().formfield(
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Pays"
    )
    
    telephone = PhoneNumberField(label="Numéro de téléphone", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ex: +237 6xx xxx xxx'
    }))

    email = forms.EmailField(label="Adresse Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Client
        fields = [
            'nom_entreprise', 'interlocuteur', 'pays', 'telephone', 'ville', 'rue', 'bp',
            'secteur_activite', 'origine_client', 'type_client'
        ]
        widgets = {
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom de l'entreprise"}),
            'interlocuteur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom du contact"}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ville"}),
            'rue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Rue"}),
            'bp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Boîte postale"}),
            'secteur_activite': forms.Select(attrs={'class': 'form-control'}),
            'origine_client': forms.Select(attrs={'class': 'form-control'}),
            'type_client': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.commercial_user = kwargs.pop('commercial_user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def save(self, commit=True):
        try:
            user = User(
                username=self.cleaned_data['nom_entreprise'], 
                email=self.cleaned_data['email'],
                role='client',
                is_active=False
            )
            user.set_unusable_password()
            if commit:
                user.save()
        except Exception as e:
            raise forms.ValidationError(f"Erreur lors de la création de l'utilisateur : {str(e)}")

        client = super().save(commit=False)
        client.user = user  
        if self.commercial_user:
            client.commercial = self.commercial_user
        if commit:
            client.save()
        return client

class CommercialRegistrationForm(forms.Form):
    nom_commercial = forms.CharField(label="Nom du commercial", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    contact = forms.CharField(label="Contact", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['nom_commercial'],
            email=self.cleaned_data['email'],
            role='commercial',
            is_active=False
        )
        user.set_unusable_password()
        if commit:
            user.save()

        commercial = Commercial(
            user=user,
            nom_commercial=self.cleaned_data['nom_commercial'],
            contact=self.cleaned_data['contact']
        )
        if commit:
            commercial.save()
        return commercial

class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom_entreprise', 'interlocuteur', 'telephone', 'pays', 'ville', 'rue', 'bp']
        widgets = {
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'interlocuteur': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'rue': forms.TextInput(attrs={'class': 'form-control'}),
            'bp': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ClientRegistrationCmcForm(forms.ModelForm):
    
    commercial = forms.ModelChoiceField(
        queryset=Commercial.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'placeholder': "Assigner un commercial"}),
        required=True,
    )
    pays = CountryField().formfield(
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Pays"
    )
    
    telephone = PhoneNumberField(label="Numéro de téléphone", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ex: +237 6xx xxx xxx'
    }))

    email = forms.EmailField(label="Adresse Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Client
        fields = [
            'nom_entreprise', 'interlocuteur', 'pays', 'telephone', 'ville', 'rue', 'bp',
            'secteur_activite', 'origine_client', 'type_client', 'commercial',
        ]
        widgets = {
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom de l'entreprise"}),
            'interlocuteur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom du contact"}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ville"}),
            'rue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Rue"}),
            'bp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Boîte postale"}),
            'secteur_activite': forms.Select(attrs={'class': 'form-control'}),
            'origine_client': forms.Select(attrs={'class': 'form-control'}),
            'type_client': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.commercial_user = kwargs.pop('commercial_user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def save(self, commit=True):
        email = self.cleaned_data['email']
        username = self.cleaned_data['nom_entreprise']

        user = User(
            username=username,
            email=email,
            role='client',
            is_active=False
        )
        user.set_unusable_password()
        if commit:
            user.save()

        client = super().save(commit=False)
        client.user = user
        if commit:
            client.save()
        return client