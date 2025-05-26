from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404
from documents.models import GeneratedDoc,Document
from accounts.models import Commercial,ChefCommercial,Client
from devis.models import DevisNouveauProduit
from proforma.models import Proforma
from django.utils import timezone
from django.contrib import messages
from django.core.files.base import ContentFile
from orders.models import Commande
from .forms import DocumentUploadForm
from django.core.paginator import Paginator
from django.db.models import Prefetch
from utils.emails import envoyer_email_notification

@login_required
def ouvrir_devis(request, doc_id):
    document = get_object_or_404(GeneratedDoc, id=doc_id, type_doc='devis')

    try:
        # Vous récupérez le devis associé via la clé étrangère dans DevisNouveauProduit
        devis = DevisNouveauProduit.objects.select_related('client__commercial').get(generated_doc=document)
    except DevisNouveauProduit.DoesNotExist:
        raise Http404("Aucun devis associé à ce document.")

    try:
        commercial = Commercial.objects.get(user=request.user)
    except Commercial.DoesNotExist:
        return HttpResponseForbidden("Vous n'êtes pas un commercial.")

    if devis.client.commercial != commercial:
        return HttpResponseForbidden("Accès non autorisé à ce devis.")

    if not devis.lu:
        devis.lu = True
        devis.save(update_fields=['lu'])

    if document.doc:
        return FileResponse(document.doc.open('rb'), content_type='application/pdf')
    else:
        raise Http404("Fichier PDF introuvable.")
    
@login_required
def upload_document(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.commande = commande
            document.client = commande.client
            document.uploaded_by = request.user
            document.fichier = request.FILES['fichier']  # Associe le fichier
            document.date_upload = timezone.now()
            document.save()
            chef_commercial=ChefCommercial.objects.get(pk=1)
            # Marquer la commande comme livrée si une facture est uploadée
            if document.type_documents == 'facture':
                commande.statut = 'delivered'
                commande.save()
            envoyer_email_notification(
                "Nouveau document ajouté",
                f"Un nouveau document a été ajouté à la commande #{commande.id}.",
                [commande.client.user.email, chef_commercial.user.email]
            )
            return redirect('commande_detail', commande_id=commande.id)
    else:
        form = DocumentUploadForm()

    return render(request, 'documents/upload_document.html', {
        'form': form,
        'commande': commande
    })
@login_required
def mes_documents(request):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        return HttpResponseForbidden("Vous devez être un client pour accéder à vos documents.")

    commandes = Commande.objects.filter(client=client).order_by('-date_creation')

    commandes_avec_docs = []
    for commande in commandes:
        uploaded_docs = commande.documents.all().order_by('-date_upload')

        # Récupérer les proformas générés liés à cette commande
        proformas = GeneratedDoc.objects.filter(
            type_doc='proforma',
            commande=commande
        ).order_by('-date_creation')

        commandes_avec_docs.append({
            'commande': commande,
            'uploaded_documents': uploaded_docs,
            'proformas': proformas,
        })

    paginator = Paginator(commandes_avec_docs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'documents/mes_documents.html', {
        'page_obj': page_obj
    })
@login_required
def be_documents(request):
    devis_gen = GeneratedDoc.objects.filter(type_doc='devis').order_by('-date_creation')
    paginator = Paginator(devis_gen,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'documents/be_documents.html', {
        'page_obj': page_obj
    })
@login_required
def commercial_documents(request):
    try:
        commercial = Commercial.objects.get(user=request.user)
    except Commercial.DoesNotExist:
        return HttpResponseForbidden("Vous devez être un commercial pour accéder à vos documents.")

    clients = Client.objects.filter(commercial=commercial)

    # Organize documents by client
    clients_with_docs = []
    for client in clients:
        commandes = Commande.objects.filter(client=client).order_by('-date_creation')
        commandes_data = []

        for commande in commandes:
            uploaded_docs = commande.documents.all().order_by('-date_upload')
            proformas = GeneratedDoc.objects.filter(type_doc='proforma', proforma__commande=commande).order_by('-date_creation')
            commandes_data.append({
                'commande': commande,
                'uploaded_documents': uploaded_docs,
                'proformas': proformas,
            })

        if commandes_data:
            clients_with_docs.append({
                'client': client,
                'commandes': commandes_data,
            })

    paginator = Paginator(clients_with_docs, 5)  # Show 5 clients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'documents/commercial_documents.html', {
        'page_obj': page_obj
    })

@login_required
def cmc_documents(request):
    try:
        cmc = ChefCommercial.objects.get(user=request.user)
    except ChefCommercial.DoesNotExist:
        return HttpResponseForbidden("Vous devez être le chef commercial pour accéder à vos documents.")

    clients = Client.objects.all()

    clients_with_docs = []
    for client in clients:
        commandes = Commande.objects.filter(client=client).order_by('-date_creation')
        commandes_data = []

        for commande in commandes:
            uploaded_docs = commande.documents.all().order_by('-date_upload')
            proformas = GeneratedDoc.objects.filter(type_doc='proforma', proforma__commande=commande).order_by('-date_creation')
            commandes_data.append({
                'commande': commande,
                'uploaded_documents': uploaded_docs,
                'proformas': proformas,
            })

        if commandes_data:
            clients_with_docs.append({
                'client': client,
                'commandes': commandes_data,
            })
    paginator = Paginator(clients_with_docs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'documents/cmc_documents.html', {
        'page_obj': page_obj
    })