from .forms import ProformaNouveauProduitForm, RefusCommentaireForm, ProformaOldProduitForm
from accounts.models import Client, Commercial, ChefCommercial
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.utils import timezone
from . models import DevisNouveauProduit,Proforma,Produit,ProduitQuote,ProduitQuoteItem,ProformaItem,CoordonneeBancaire
from documents.models import GeneratedDoc
from django.core.files.base import ContentFile
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from decimal import Decimal
from num2words import num2words
from utils.emails import envoyer_email_notification
from django.core.paginator import Paginator
from itertools import chain
from operator import attrgetter
from django.db import models

@login_required
def creer_proforma_nouveau_produit(request, devis_id):
    devis = get_object_or_404(DevisNouveauProduit, id=devis_id)
    if request.method == "POST":
        form = ProformaNouveauProduitForm(request.POST)
        if form.is_valid():
            prix_unitaire = form.cleaned_data['prix_unitaire']
            modalites_reglement = form.cleaned_data['modalites_reglement']
            condition_ht = form.cleaned_data['condition_ht']
            client = devis.client

            quantite = devis.quantite_previsionnelle
            montant_total_ht = quantite * prix_unitaire

            # TVA depends on client type
            tva = 0
            if client.type_client == 'local':
                tva = montant_total_ht * Decimal('0.1925') # 19.25% TVA

            net_a_payer = montant_total_ht + tva
            net_a_payer_lettres = num2words(net_a_payer, lang='fr').capitalize()

            proforma = Proforma.objects.create(
                client=client,
                modalites_reglement=modalites_reglement,
                condition_ht= condition_ht,
                montant_total_ht=montant_total_ht,
                tva=tva,
                net_a_payer=net_a_payer,
                net_a_payer_lettres=net_a_payer_lettres,
                statut='en_attente'
            )

            ProformaItem.objects.create(
                proforma=proforma,
                produit=None,
                designation=devis.designation_produit,
                quantite=quantite,
                unite=devis.unite,
                prix_unitaire=prix_unitaire,
                montant=montant_total_ht
            )
            proforma_items= ProformaItem.objects.get(proforma=proforma)
            banque= CoordonneeBancaire.objects.all()
            # generate PDF
            context = {
               'proforma': proforma,
               'proforma_items': proforma_items,
               'banque': banque
            }
            html = render_to_string('proforma/proforma_template.html', context)
            result = BytesIO()
            pdf_status = pisa.CreatePDF(html, dest=result)
            if not pdf_status.err:
                pdf_file = ContentFile(result.getvalue(), name='f"proforma_{proforma.id}.pdf"')
                generated_doc = GeneratedDoc.objects.create(
                    generated_by= request.user,
                    doc=pdf_file,
                    type_doc='proforma',
                    
                    date_creation=timezone.now()
                )
            proforma.devis=devis
            proforma.generated_doc = generated_doc
            proforma.save()
            devis.statut='finalise'
            devis.save()
            messages.success(request, "Proforma créée avec succès.")
            return redirect('visualiser_proforma', proforma_id=proforma.id)
    else:
        form = ProformaNouveauProduitForm()

    return render(request, 'proforma/creer_offre.html', {
        'form': form,
        'devis': devis
    })

@login_required
def creer_proforma_old(request, quote_id):
    quote = get_object_or_404(ProduitQuote, id=quote_id)

    if request.user != quote.client.commercial.user:
        return HttpResponseForbidden("Non autorisé à créer une proforma pour cette demande.")

    items = quote.items.select_related('produit')
    client = quote.client

    if request.method == 'POST':
        form = ProformaOldProduitForm(request.POST, items=items)
        if form.is_valid():
            modalites = form.cleaned_data['modalites_reglement']
            condition_ht = form.cleaned_data.get('condition_ht', '')

            montant_total_ht = Decimal('0.0')

            # On crée d'abord la proforma sans les champs calculés
            proforma = Proforma.objects.create(
                client=client,
                quote=quote,
                modalites_reglement=modalites,
                condition_ht=condition_ht,
                montant_total_ht=Decimal('0.0'),  # temporaire
                tva=Decimal('0.0'),               # temporaire
                net_a_payer=Decimal('0.0'),       # temporaire
                net_a_payer_lettres='',
                statut='en_attente'
            )

            for item in items:
                prix_unitaire = form.cleaned_data.get(f"prix_{item.id}")
                item_total = item.quantite * prix_unitaire
                montant_total_ht += item_total

                ProformaItem.objects.create(
                    proforma=proforma,
                    produit=item.produit,
                    designation=item.produit.designation,
                    quantite=item.quantite,
                    unite=item.unite,
                    prix_unitaire=prix_unitaire,
                    montant=item_total
                )

            # TVA selon type client
            tva = Decimal('0.0')
            if client.type_client == 'local':
                tva = montant_total_ht * Decimal('0.1925')

            net_a_payer = montant_total_ht + tva
            net_a_payer_lettres = num2words(net_a_payer, lang='fr').capitalize()

            # Mise à jour de la proforma avec les bons totaux
            proforma.montant_total_ht = montant_total_ht
            proforma.tva = tva
            proforma.net_a_payer = net_a_payer
            proforma.net_a_payer_lettres = net_a_payer_lettres
            proforma.save()

            # Génération du PDF
            context = {
                'proforma': proforma,
                'proforma_items': proforma.items.all(),
                'banque': CoordonneeBancaire.objects.all()
            }
            html = render_to_string('proforma/proforma_template.html', context)
            result = BytesIO()
            pisa_status = pisa.CreatePDF(html, dest=result)

            if not pisa_status.err:
                pdf_file = ContentFile(result.getvalue(), name=f"proforma_{proforma.id}.pdf")
                doc = GeneratedDoc.objects.create(
                    generated_by=request.user,
                    doc=pdf_file,
                    type_doc='proforma',
                    date_creation=timezone.now()
                )
                proforma.generated_doc = doc
                proforma.save()

            messages.success(request, "Proforma créée avec succès.")
            return redirect('visualiser_proforma', proforma_id=proforma.id)

    else:
        form = ProformaOldProduitForm(items=items)

    return render(request, 'proforma/creer_proforma_old.html', {
        'form': form,
        'quote': quote,
        'items': items
    })

@login_required
def visualiser_proforma(request, proforma_id):
    proforma = get_object_or_404(Proforma, pk=proforma_id)
    return render(request, 'proforma/visualiser_proforma.html', {
        'proforma': proforma
    })

@require_POST
def envoyer_proforma(request, proforma_id):
    proforma = get_object_or_404(Proforma, pk=proforma_id)
    proforma.statut = 'en_attente'
    proforma.date_envoie = timezone.now()
    proforma.save()
    chef_commercial=ChefCommercial.objects.get(pk=1)
    messages.success(request, "Proforma envoyé au CMC avec succès.")
    envoyer_email_notification(
        "Proforma à valider",
        f"La proforma #{proforma.id} du client {proforma.client.nom_entreprise} est en attente de validation.",
        [chef_commercial.user.email]
    )
    return redirect('commercial_dashboard')

@login_required
def proforma_devis(request, devis_id):
    devis = get_object_or_404(DevisNouveauProduit, pk=devis_id)

    if devis.client.commercial.user != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à voir les offres pour ce devis.")

    offres = Proforma.objects.filter(devis=devis).order_by('-date_envoie') 
    item_list = ProformaItem.objects.filter(proforma__in=offres)

    return render(request, 'proforma/liste_proforma.html', {'devis': devis, 'offres': offres, 'item_list': item_list})

@login_required
def proforma_quote(request, quote_id):
    quote = get_object_or_404(ProduitQuote, pk=quote_id)

    if request.user != quote.client.commercial.user:
        return HttpResponseForbidden("Accès interdit à ces offres.")

    offres = Proforma.objects.filter(quote=quote).select_related('client').prefetch_related('items')

    return render(request, 'proforma/liste_proforma_quote.html', {
        'quote': quote,
        'offres': offres,
    })


@login_required
def valider_proforma_cmc(request, proforma_id):
    offer = get_object_or_404(Proforma, pk=proforma_id)
    offer.statut = 'valide'
    offer.save()
    messages.success(request, "Proforma validée avec succès.")
    if offer.devis:
        envoyer_email_notification(
            "Nouvelle Proforma",
            f"Vous aves reçu la proforma de la demande de devis du produit {offer.devis.designation_produit}.",
            [offer.client.user.email]
        )
    else:
         envoyer_email_notification(
            "Nouvelle Proforma",
            f"Vous aves reçu la proforma de la demande de cotation numéro {offer.quote}.",
            [offer.client.user.email]
        )
    return redirect('list_proforma')

@login_required
def refuser_proforma_cmc(request, proforma_id):
    offer = get_object_or_404(Proforma, pk=proforma_id)
    if request.method == 'POST':
        form = RefusCommentaireForm(request.POST)
        if form.is_valid():
            offer.statut = 'non_valide'
            offer.commentaire_refus_cmc = form.cleaned_data['commentaire_refus']
            offer.save()
            messages.success(request, "Proforma refusée avec commentaire.")
            return redirect('list_proforma')
    else:
        form = RefusCommentaireForm()

    return render(request, 'proforma/refuser_proforma.html', {'form': form, 'offer': offer})

@login_required
def list_proforma(request):
    proformas = Proforma.objects.filter(statut='en_attente').prefetch_related('items').select_related('client', 'devis__generated_doc').order_by('-date_envoie')
    return render(request, 'proforma/liste_proforma_cmc.html', {'proformas': proformas})

@login_required
def offres_client(request):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        return HttpResponseForbidden("Vous n’êtes pas un client.")

    # Fetch separately
    proformas_nouveaux = Proforma.objects.filter(
        client=client,
        devis__isnull=False,
        statut="valide"
    ).select_related('devis').order_by('-date_envoie')

    proformas_anciens = Proforma.objects.filter(
        client=client,
        quote__isnull=False,
        statut="valide"
    ).select_related('quote').order_by('-date_envoie')

    # Annotate each with type (not database annotation — just a Python field)
    for p in proformas_nouveaux:
        p.produit_type = "🆕 Nouveau produit"

    for p in proformas_anciens:
        p.produit_type = "🧾 Produit existant"

    # Merge and sort all proformas by date_envoie descending
    all_proformas = sorted(
        chain(proformas_nouveaux, proformas_anciens),
        key=attrgetter('date_envoie'),
        reverse=True
    )

    return render(request, 'proforma/offres_client.html', {
        'all_proformas': all_proformas
    })

@login_required
def accepter_offre(request, proforma_id):
    client = Client.objects.get(user=request.user)
    proforma = get_object_or_404(Proforma, pk=proforma_id, client=client)
    
    if proforma.devis:
        # new product
        proforma.statut = 'acceptee'
        proforma.save()

        Proforma.objects.filter(devis=proforma.devis).exclude(pk=proforma.pk).update(statut='refusee')
        creer_produit_depuis_offre(proforma)
        messages.success(request, "Offre acceptée et produit ajouté au catalogue.")
    elif proforma.quote:
        # old products
        proforma.statut = 'acceptee'
        proforma.save()

        Proforma.objects.filter(quote=proforma.quote).exclude(pk=proforma.pk).update(statut='refusee')
        messages.success(request, "Offre acceptée.")
    else:
        messages.error(request, "Offre invalide.")

    return redirect('offres_client')

@login_required
def refuser_offre(request, proforma_id):
    client = Client.objects.get(user=request.user)
    proforma = get_object_or_404(Proforma, pk=proforma_id, client=client)
    if request.method == 'POST':
        form = RefusCommentaireForm(request.POST)
        if form.is_valid():
            proforma.statut = 'refusee'
            proforma.commentaire_refus_client = form.cleaned_data['commentaire_refus']
            proforma.save()
            messages.success(request, "Offre refusée.")
            return redirect('offres_client')
    else:
        form = RefusCommentaireForm()

    return render(request, 'proforma/refuser_offre.html', {'form': form, 'offer': proforma})

def creer_produit_depuis_offre(offre: Proforma):
    devis = offre.devis
    client = devis.client 
    # Supprimer les anciens produits liés à ce devis (ou offre)
    Produit.objects.filter(proforma_origine__devis=devis).delete()
    # Créer le nouveau produit
    Produit.objects.create(
        client=client,
        designation=devis.designation_produit,
        unite=devis.unite,
        categorie=devis.famille_produit,
        proforma_origine=offre
    )

@login_required
def detail_proforma_client(request, proforma_id):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        return HttpResponseForbidden("Vous n’êtes pas un client.")
    # Proformas pour les anciens produits (quote)
    proforma = get_object_or_404(Proforma, pk=proforma_id, client=client)

    return render(request, 'proforma/detail_proforma.html', {
        'proforma': proforma
    })

@login_required
def produits_client(request):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        return HttpResponseForbidden("Vous n’êtes pas un client.")
    produits = Produit.objects.filter(client=client)
    return render(request, 'commande/produits_client.html', {'produits': produits})

@login_required
def proformas_acceptees(request):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        return redirect('dashboard')

    proformas_qs = Proforma.objects.filter(
        client=client,
        statut='acceptee'
    ).select_related('generated_doc').order_by('-date_envoie')  # Latest first

    paginator = Paginator(proformas_qs, 10)  # 10 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'commande/commande.html', {
        'page_obj': page_obj
    })

@login_required
def add_to_quote(request, produit_id):
    client = Client.objects.get(user=request.user)
    produit = get_object_or_404(Produit, id=produit_id)

    # Get or create an en_attente quote
    quote, created = ProduitQuote.objects.get_or_create(client=client, statut='en_attente')

    # Add or update quantity of the product
    item, item_created = ProduitQuoteItem.objects.get_or_create(
        quote=quote,
        produit=produit,
        defaults={'quantite': 1}
    )
    if not item_created:
        item.quantite += 1
        item.save()

    return redirect('produits_client')

@login_required
def quote_view(request):
    client = Client.objects.get(user=request.user)
    quote = ProduitQuote.objects.filter(client=client, statut='en_attente').first()

    elements = quote.items.select_related('produit') if quote else []
    return render(request, 'proforma/quote_view.html', {
        'elements': elements,
        'quote': quote
    })

@login_required
def remove_from_quote(request, item_id):
    client = Client.objects.get(user=request.user)
    item = get_object_or_404(ProduitQuoteItem, id=item_id, quote__client=client)
    item.delete()
    return redirect('quote_view')

@login_required
def cancel_quote(request):
    client = Client.objects.get(user=request.user)
    quote = ProduitQuote.objects.filter(client=client, statut='en_attente').first()
    if quote:
        quote.delete()
    return redirect('produits_client')

@login_required
def submit_quote(request):
    client = get_object_or_404(Client, user=request.user)
    quote = ProduitQuote.objects.filter(client=client, statut='en_attente').first()

    if not quote:
        messages.error(request, "Aucune demande de devis en attente à soumettre.")
        return redirect('client_dashboard')

    if request.method == 'POST':
        # Update each item from POST data
        for item in quote.items.all():
            quantite = request.POST.get(f'quantite_{item.id}')
            unite = request.POST.get(f'unite_{item.id}')
            if quantite and quantite.isdigit():
                item.quantite = int(quantite)
            if unite in ['kg', 'pièce']:
                item.unite = unite
            item.save()

        quote.statut = 'en_traitement'
        quote.save()
        envoyer_email_notification(
            "Nouvelle demande de cotation",
            f"Le client {quote.client.nom_entreprise} a soumis une nouvelle demande de cotation.",
            [quote.client.commercial.user.email]
        )
        messages.success(request, "Votre demande de devis a été envoyée au commercial.")

    return redirect('client_dashboard')

@login_required
def liste_quotes(request):
    try:
        commercial = Commercial.objects.get(user=request.user)
    except Commercial.DoesNotExist:
        return HttpResponseForbidden("Vous n'êtes pas un commercial.")

    quotes = ProduitQuote.objects.filter(client__commercial=commercial, statut='en_traitement')
    return render(request, 'proforma/liste_quotes.html', {'quotes': quotes})

@login_required
def detail_quote(request, quote_id):
    quote = get_object_or_404(ProduitQuote, pk=quote_id)

    if request.user != quote.client.commercial.user:
        return HttpResponseForbidden("Accès refusé.")

    items = quote.items.select_related('produit')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'creer_proforma':
            return redirect('creer_proforma_old', quote_id=quote.id)
        elif action == 'retour':
            quote.statut = 'en_traitement'
            quote.save()
            messages.info(request, "La demande a été marquée comme en traitement.")
            return redirect('liste_quotes')

    return render(request, 'proforma/detail_quote.html', {
        'quote': quote,
        'items': items
    })

@login_required
def liste_devis_et_quotes(request):
    try:
        commercial = Commercial.objects.get(user=request.user)
    except Commercial.DoesNotExist:
        return HttpResponseForbidden("Vous n'êtes pas un commercial.")

    devis_qs = DevisNouveauProduit.objects.filter(client__commercial=commercial).annotate(
        type_label=models.Value("devis", output_field=models.CharField())
    )

    quotes_qs = ProduitQuote.objects.filter(client__commercial=commercial).annotate(
        type_label=models.Value("quote", output_field=models.CharField())
    )

    # Annoter manuellement le nombre de proformas
    for devis in devis_qs:
        devis.nb_proformas = devis.proformas.count()  # requires related_name="proformas" in model

    for quote_instance in quotes_qs:
        quote_instance.nb_proformas = quote_instance.proformas.count()  # idem

    combined_list = sorted(
        chain(devis_qs, quotes_qs),
        key=lambda obj: obj.date_creation,
        reverse=True
    )

    paginator = Paginator(combined_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "proforma/liste_devis_et_quotes.html", {
        "page_obj": page_obj
    })