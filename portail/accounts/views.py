from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login,get_user_model,logout
from django.contrib import messages
from .forms import (
    ClientRegistrationForm, UserLoginForm, CommercialRegistrationForm,
    ClientProfileForm,LeadRegistrationForm,SetPasswordForm,ClientRegistrationCmcForm
)
from .models import User, Client, Commercial, LeadRequest, ChefCommercial
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from utils.emails import envoyer_email_notification


User = get_user_model()

def home(request):
    return render(request, 'dashboard/home.html')

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, "Connexion réussie!")
                    # Redirection par rôle
                    if user.role.lower() in ['client']: 
                        return redirect('client_dashboard')
                    elif  user.role.lower() in ['commercial']:
                        return redirect('commercial_dashboard')
                    elif  user.role.lower() in ['chef_commercial']:
                        return redirect('chef_dashboard')
                    elif  user.role.lower() in ['be']:
                        return redirect('be_dashboard')
                else:
                    messages.error(request, "Votre compte est désactivé.")
                    return redirect('login')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def register_client(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST,commercial_user=request.user)
        if form.is_valid():
            client = form.save()
            user=client.user.set_unusable_password()
            user.save()
            send_activation_email(user, request)
            messages.success(request, "Le compte client a été créé. Un lien d'activation a été envoyé.")
            return redirect('commercial_dashboard')  
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = ClientRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def register_client_cmc(request):
    if request.method == 'POST':
        form = ClientRegistrationCmcForm(request.POST)
        if form.is_valid():
            client = form.save()  
            send_activation_email(client.user, request)  
            messages.success(request, "Le compte client a été créé. Un lien d'activation a été envoyé.")
            return redirect('liste_client_cmc')  
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ClientRegistrationCmcForm()

    return render(request, 'accounts/register_client_cmc.html', {'form': form})

@login_required
def lead_validation(request, lead_id):
    lead = get_object_or_404(LeadRequest, id=lead_id)

    if request.method == 'POST':
        form = ClientRegistrationCmcForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.nom_entreprise = lead.raison_sociale
            client.interlocuteur = lead.interlocuteur
            client.user.email=lead.email
            client.pays = lead.pays
            client.ville = lead.ville
            client.rue = lead.rue
            client.telephone = lead.telephone
            client.bp = lead.bp
            client.secteur_activite = lead.secteur_activite
            client.origine_client = lead.origine_client
            client.save()
            
            lead.converted = True 
            lead.save()
            
            send_activation_email(client.user, request)
            messages.success(request, "Le lead a été validé et converti en client.")
            return redirect('chef_dashboard')
    else:
        # Pre-fill the form with lead data
        form = ClientRegistrationCmcForm(initial={
            'nom_entreprise': lead.raison_sociale,
            'interlocuteur': lead.interlocuteur,
            'email': lead.email,  # <-- Make sure this field exists on the form
            'pays': lead.pays,
            'ville': lead.ville,
            'rue': lead.rue,
            'telephone': lead.telephone,
            'bp': lead.bp,
            'secteur_activite': lead.secteur_activite,
            'origine_client': lead.origine_client,
        })

    return render(request, 'accounts/register_client_cmc.html', {
        'form': form,
        'from_lead': True,
        'lead': lead,
    })

@login_required
def refuser_lead(request, lead_id):
    lead = get_object_or_404(LeadRequest, id=lead_id)
    lead.valide=False
    lead.save()
    messages.success(request, "Le lead a été supprimé.")
    return redirect('leads_list')

@login_required
def register_commercial(request):
    if request.method == 'POST':
        form = CommercialRegistrationForm(request.POST)
        if form.is_valid():
            commercial = form.save()
            send_activation_email(commercial.user, request)
            messages.success(request, "Le compte commercial a été créé. Un lien d'activation a été envoyé.")
            return redirect('chef_dashboard')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CommercialRegistrationForm()
    return render(request, 'accounts/com_register.html', {'form': form})

def send_activation_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = request.build_absolute_uri(
        reverse('set_password', kwargs={'uidb64': uid, 'token': token})
    )

    subject = "Activation de votre compte"
    message = (
        f"Bonjour {user.username},\n\n"
        f"Veuillez définir votre mot de passe en cliquant sur ce lien :\n{activation_link}\n\n"
        f"Ce lien est à usage unique et expirera sous peu."
    )

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False
    )

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                user.is_active = True  # Activate account now
                user.save()
                messages.success(request, "Mot de passe défini. Votre compte est activé.")
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'accounts/password.html', {'form': form})

    messages.error(request, "Lien invalide ou expiré.")
    return redirect('home')

@login_required
def profile_view(request):
    if request.user.role != 'client':
        return redirect('unauthorized')

    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ClientProfileForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile_view')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = ClientProfileForm(instance=client)

    return render(request, 'accounts/profile_view.html', {'form': form})


@login_required
def resend_client_invitation(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    user = client.utilisateur

    if user.is_active:
        messages.info(request, "Ce client a déjà activé son compte.")
        return redirect('client_list')

    send_activation_email(user, request)
    messages.success(request, "Nouvelle invitation envoyée.")
    return redirect('client_list')


def lead_request(request):
    if request.method == 'POST':
        form = LeadRegistrationForm(request.POST)
        if form.is_valid():
            lead=form.save()
            messages.success(request, "Votre demande a été enregistrée.")
            chef_commercial=ChefCommercial.objects.get(pk=1)
            """
            envoyer_email_notification(
                "Proforma à valider",
                f"La requete de creation de compte du prospect de {lead.raison_sociale} est en attente de validation.",
                [chef_commercial.user.email]
            )"""
            return redirect('home')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = LeadRegistrationForm()
    return render(request, 'accounts/leads.html', {'form': form})


def liste_clients(request):
    commercial = Commercial.objects.get(user=request.user)
    clients = Client.objects.filter(commercial=commercial)

    return render(request, 'accounts/client_list.html', {
        'clients': clients
    })

def liste_clients_cmc(request):
    clients = Client.objects.all()

    return render(request, 'accounts/list_client_cmc.html', {
        'clients': clients
    })

def liste_commercial(request):
    commerciaux = Commercial.objects.annotate(nb_clients=Count('clients'))
    return render(request, 'accounts/liste_commercial.html', {
        'commerciaux': commerciaux
    })

def liste_lead(request):
    leads = LeadRequest.objects.filter(valide=True, converted=False)
    return render(request, 'accounts/liste_leads.html', {
        'leads': leads
    })


def logout_user(request):
	logout(request)
	messages.success(request,"Vous vous etes déconnecté")
	return redirect('home')