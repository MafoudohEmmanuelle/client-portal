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
from datetime import timedelta, datetime
import json

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
        devis_total = DevisNouveauProduit.objects.filter(client=client).count()
        devis_status_counts = DevisNouveauProduit.objects.filter(client=client).values('statut').annotate(count=Count('id'))
        return render(request,'dashboard/client_dashboard.html',{
            'offres_en_attente': offres_en_attente , 
            'nb_produits': nb_produits,
            'commandes_pending': commandes_pending,
            'commandes_accepted': commandes_accepted,
            'commandes_delivered': commandes_delivered,
            'latest_commandes': latest_commandes,
            'docs_count': docs_count,
            'devis_total': devis_total,
            'devis_status_counts': devis_status_counts,
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

        # Devis à traiter
        unread_devis = DevisNouveauProduit.objects.filter(
            client__in=clients,
            statut__in=["nouveau", "en_traitement"]
        )

        # Quotes à traiter
        unread_quotes = ProduitQuote.objects.filter(
            client__in=clients,
            statut__in=["nouveau","en_traitement"]
        )

        # Devis complets
        complet_devis = DevisNouveauProduit.objects.filter(
            client__in=clients,
            statut="complet"
        )

        # Nouvelles commandes
        new_orders_count = Commande.objects.filter(
            client__in=clients,
            statut='en_attente'
        ).count()

        six_months_ago = datetime.now() - timedelta(days=180)

        proforma_stats_qs = (
            Proforma.objects
            .filter(client__commercial=commercial, date_envoie__gte=six_months_ago)
            .annotate(month=TruncMonth("date_envoie"))
            .values("month")
            .annotate(
                sent=Count("id"),
                accepted=Count("id", filter=Q(statut='acceptee'))
            )
            .order_by("month")
        )

        proforma_stats = [
            {
                "month": stat["month"].strftime("%b %Y"),
                "sent": stat["sent"],
                "accepted": stat["accepted"],
            }
            for stat in proforma_stats_qs
        ]

        now = datetime.now()
        commandes_par_client = (
            Commande.objects
            .filter(
                client__commercial=commercial,
                date_creation__month=now.month,
                date_creation__year=now.year
            )
            .values('client__nom_entreprise')
            .annotate(total=Count('id'))
        )

        context = {
            'clients_count': clients.count(),
            'pending_quotes_count': unread_devis.count(),
            'unread_devis': unread_devis,
            'complete_devis_count': complet_devis.count(),
            'new_orders_count': new_orders_count,
            'unread_quotes': unread_quotes.count(),
            'proforma_stats': json.dumps(proforma_stats),
            'commandes_par_client': json.dumps(list(commandes_par_client)),
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
        today = timezone.now().date()
        first_day = today.replace(day=1)
        new_proforma=Proforma.objects.filter(statut='en_attente').count()
        new_orders_count = Commande.objects.filter(statut='pending').count()
        leads_count=LeadRequest.objects.filter(valide=True, converted=False).count()
        clients_per_commercial = Client.objects.values('commercial__nom_commercial').annotate(total=Count('id'))
        commandes = Commande.objects.filter(date_creation__gte=first_day)
        commandes_per_commercial = commandes.values('client__commercial__nom_commercial').annotate(total=Count('id'))
        proforma_stats = []
        for i in range(6):
            month = today - timedelta(days=i*30)
            month_name = calendar.month_name[month.month]
            proformas = Proforma.objects.filter(date_envoie__year=month.year, date_envoie__month=month.month)
            accepted = proformas.filter(statut='acceptee').count()
            refused = proformas.filter(statut='refusee').count()
            proforma_stats.append({'month': month_name, 'accepted': accepted, 'refused': refused})
        context = {
            'clients_count': clients_count,
            'new_proforma':new_proforma,
            'new_orders_count': new_orders_count,
            'leads_count': leads_count,
            'clients_per_commercial': list(clients_per_commercial),
            'commandes_per_commercial': list(commandes_per_commercial),
            'proforma_stats': list(reversed(proforma_stats)),
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
