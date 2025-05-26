from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Commande
from proforma.models import Proforma
from documents.models import Document
from .forms import CommandeForm, BonCommandeUploadForm
from accounts.models import Client,Commercial
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import Http404
from utils.emails import envoyer_email_notification

@login_required
def passer_commande_depuis_proforma(request, proforma_id):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        raise Http404("Aucun client associé à cet utilisateur.")

    proforma = get_object_or_404(Proforma, id=proforma_id, client=client, statut='acceptee')

    if request.method == 'POST':
        commande_form = CommandeForm(request.POST)
        bon_form = BonCommandeUploadForm(request.POST, request.FILES)

        if commande_form.is_valid() and bon_form.is_valid():
            commande = commande_form.save(commit=False)
            commande.client = client
            commande.proforma = proforma
            commande.date_creation = timezone.now()
            commande.statut = 'en_attente'
            commande.save()

            # Associer la commande au document généré de la proforma
            if proforma.generated_doc:
                proforma.generated_doc.commande = commande
                proforma.generated_doc.save()

            # Enregistrer le bon de commande comme document lié
            document = bon_form.save(commit=False)
            document.commande = commande
            document.client = client
            document.uploaded_by = request.user
            document.type_documents = 'bon_commande'
            document.date_upload = timezone.now()
            document.save()

            envoyer_email_notification(
                "Nouvelle commande",
                f"Le client {commande.client.nom_entreprise} a passé une nouvelle commande.",
                [commande.client.commercial.user.email]
            )

            return redirect('proformas_acceptees')
    else:
        commande_form = CommandeForm()
        bon_form = BonCommandeUploadForm()

    return render(request, 'commande/passer_commande.html', {
        'proforma': proforma,
        'commande_form': commande_form,
        'bon_form': bon_form
    })

@login_required
def commandes_client(request):
    client = Client.objects.get(user=request.user)
    statut_filtre = request.GET.get('statut', 'toutes')

    commandes = Commande.objects.filter(client=client).order_by('-date_creation')

    if statut_filtre != 'toutes':
        commandes = commandes.filter(statut=statut_filtre)

    paginator = Paginator(commandes, 10)  # 10 commandes par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'statut_filtre': statut_filtre,
    }
    return render(request, 'commande/commande_client.html', context)

@login_required
def commande_detail_client(request, id_commande):
    client = Client.objects.get(user=request.user)
    commande = get_object_or_404(Commande, id=id_commande, client=client)
    documents = commande.documents.all()
    proforma = getattr(commande, 'proforma_origine', None)
    generated_proforma = getattr(proforma, 'generated_doc', None) if proforma else None

    return render(request, 'commande/commande_detail.html', {
        'commande': commande,
        'documents': documents,
        'generated_proforma': generated_proforma,
    })

@login_required
def valider_commande_view(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)

    # Récupérer le bon de commande associé
    bon_de_commande = commande.documents.filter(type_documents='bon_commande').first()

    if request.method == 'POST':
        if 'accept' in request.POST:
            commande.statut = 'accepted'
            commande.save()
            messages.success(request, "Commande acceptée avec succès.")
            return redirect('liste_commandes')

        elif 'refuse' in request.POST:
            commentaire = request.POST.get('commentaire')
            commande.commentaire = commentaire
            commande.statut = 'rejected'
            commande.save()
            messages.warning(request, "Commande refusée avec commentaire.")
            return redirect('liste_commandes')

    return render(request, 'commande/validation_commande.html', {
        'commande': commande,
        'bon_de_commande': bon_de_commande
    })

@login_required
def liste_commandes(request):
    commercial = Commercial.objects.get(user=request.user)
    all_commandes = Commande.objects.filter(client__commercial=commercial).order_by('-date_creation')
    paginator = Paginator(all_commandes, 10)  # 10 commandes par page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'commande/liste_commande.html', {'page_obj': page_obj})

@login_required
def commande_detail(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)  
    documents = commande.documents.all()

    return render(request, 'commande/commande_detail_commercial.html', {
        'commande': commande,
        'documents': documents
    })

@login_required
def liste_commandes_cmc(request):
    all_commandes = Commande.objects.all().order_by('-date_creation')
    paginator = Paginator(all_commandes, 10)  # 10 commandes par page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'commande/liste_commande_cmc.html', {'page_obj': page_obj})
