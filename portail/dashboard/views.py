from django.shortcuts import render,redirect
from django.http import HttpResponseForbidden
from devis.models import DevisNouveauProduit
from accounts.models import Client,Commercial,ChefCommercial,BE,LeadRequest
from proforma.models import Produit,Proforma,ProduitQuote,ProduitQuoteItem
from orders.models import Commande
from documents.models import Document
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models import Count
import calendar
from django.db.models import Q
from django.utils import timezone

def commandes_par_mois(request):
    client = Client.objects.get(user=request.user)
    commandes = (
        Commande.objects.filter(client=client)
        .annotate(month=TruncMonth('date_creation'))
        .values('month')
        .annotate(nombre=Count('id'))
        .order_by('month')
    )

    labels = []
    data = []

    for entry in commandes:
        month_name = calendar.month_name[entry['month'].month]
        labels.append(month_name)
        data.append(entry['nombre'])

    return JsonResponse({
        'labels': labels,
        'data': data,
    })

def commandes_par_client(request):
    try:
        commercial = request.user.commercial
    except:
        return JsonResponse({'labels': [], 'data': []})

    now = timezone.now()
    start_month = now.replace(day=1)
    clients = Client.objects.filter(commercial=commercial)

    labels = []
    data = []

    for client in clients:
        count = Commande.objects.filter(
            client=client,
            statut='delivered',
            date_creation__gte=start_month
        ).count()

        if count > 0:
            labels.append(client.nom_entreprise)
            data.append(count)

    return JsonResponse({'labels': labels, 'data': data})

def client_dashboard(request):
    if request.user.is_authenticated:
        try:
            client = Client.objects.get(user=request.user)
        except Client.DoesNotExist:
            return HttpResponseForbidden("Vous n'êtes pas un client.")

        offres_en_attente = Proforma.objects.filter(
            Q(client=client),
            Q(statut='valide')
        ).count()
        nb_produits = Produit.objects.filter(client=client).count()
        commandes_pending = Commande.objects.filter(client=client, statut='pending').count()
        commandes_accepted = Commande.objects.filter(client=client, statut='accepted').count()
        commandes_delivered = Commande.objects.filter(client=client, statut='delivered').count()
        latest_commandes = Commande.objects.filter(client=client).order_by('-date_creation')[:5]
        docs_count = Document.objects.filter(commande__client=client).count()
        return render(request,'dashboard/client_dashboard.html',{
            'offres_en_attente': offres_en_attente , 
            'nb_produits': nb_produits,
            'commandes_pending': commandes_pending,
            'commandes_accepted': commandes_accepted,
            'commandes_delivered': commandes_delivered,
            'latest_commandes': latest_commandes,
            'docs_count': docs_count,
            })
    else:
        return redirect('user_login')

def commercial_dashboard(request):
    if request.user.is_authenticated:
        try:
            commercial = Commercial.objects.get(user=request.user)
        except Commercial.DoesNotExist:
            return HttpResponseForbidden("Vous n'êtes pas un commercial.")

        clients = Client.objects.filter(commercial=commercial)

        # Devis à traiter (non complets)
        unread_devis = DevisNouveauProduit.objects.filter(
            client__in=clients,
            statut__in=["nouveau", "en_traitement"]
        )

        # Quotes à traiter
        unread_quotes = ProduitQuote.objects.filter(
            client__in=clients,
            statut__in=["en_traitement"]
        )

        # Devis complets (retour du BE)
        complet_devis = DevisNouveauProduit.objects.filter(
            client__in=clients,
            statut="complet"
        )

        # Commandes en attente
        new_orders_count = Commande.objects.filter(
            client__in=clients,
            statut='en_attente'
        ).count()

        # Proforma par statut (pour le suivi)
        proformas = Proforma.objects.filter(client__in=clients)
        proformas_en_attente = proformas.filter(statut='en_attente').count()
        proformas_valide = proformas.filter(statut='valide').count()
        proformas_acceptee = proformas.filter(statut='acceptee').count()
        proformas_refusee = proformas.filter(statut='refusee').count()
        proformas_non_valide = proformas.filter(statut='non_valide').count()

        # Dernières proformas (5 plus récentes)
        latest_proformas = proformas.select_related('client').order_by('-date_envoie')[:5]

        context = {
            'clients_count': clients.count(),
            'pending_quotes_count': unread_devis.count(),
            'unread_devis': unread_devis,
            'complete_devis_count': complet_devis.count(),
            'new_orders_count': new_orders_count,
            'unread_quotes': unread_quotes.count(),
            'proformas_en_attente': proformas_en_attente,
            'proformas_valide': proformas_valide,
            'proformas_acceptee': proformas_acceptee,
            'proformas_refusee': proformas_refusee,
            'proformas_non_valide': proformas_non_valide,
            'latest_proformas': latest_proformas,
        }
        return render(request, 'dashboard/commercial_dashboard.html', context)
    else:
        return redirect('user_login')
    
def chef_dashboard(request):
    if request.user.is_authenticated:
        try:
            cmc = ChefCommercial.objects.get(user=request.user)
        except ChefCommercial.DoesNotExist:
            return HttpResponseForbidden("Vous n'êtes pas le chef du commercial.")
        clients_count=Client.objects.all().count()
        new_proforma=Proforma.objects.filter(statut='en_attente').count()
        new_orders_count = Commande.objects.filter(statut='pending').count()
        leads_count=LeadRequest.objects.filter(valide=True, converted=False).count()
        context = {
            'clients_count': clients_count,
            'new_proforma':new_proforma,
            'new_orders_count': new_orders_count,
            'leads_count': leads_count
        }
        return render(request,'dashboard/chef_dashboard.html',context)
    else:
        return redirect('user_login')

def be_dashboard(request):
    if request.user.is_authenticated:
        unread_devis = DevisNouveauProduit.objects.filter(
         statut__in=["envoye_be", "en_traitement_be"]
        )
        return render(request,'dashboard/be_dashboard.html',context={'unread_devis': unread_devis,})
    else:
        return redirect('user_login')
