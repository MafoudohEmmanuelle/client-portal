from formtools.wizard.views import SessionWizardView
from .forms import DevisForm,FinitionConditionnementForm,SupportFormSet,BEDevisForm, ColorationFormSet,OutillageFormSet, CotationFormSet
from accounts.models import Client,Commercial,BE
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from . models import DevisNouveauProduit,Support,AnalyseTechniqueBE,Coloration,Outillage,Cotation
from documents.models import GeneratedDoc
from django.core.files.base import ContentFile
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from utils.emails import envoyer_email_notification

class DevisWizard(SessionWizardView): 
    form_list = [
        ("devis", DevisForm),
        ("finition", FinitionConditionnementForm),
    ]
    template_name = 'devis/devis_form.html'

    def done(self, form_list, **kwargs):
        try:
            client = Client.objects.get(user=self.request.user)
        except Client.DoesNotExist:
            return redirect('client_dashboard')

        devis_form = form_list[0]
        finition_form = form_list[1]
        # Save finition
        finition = finition_form.save()
        # Create Devis instance without saving
        devis = devis_form.save(commit=False)
        devis.client = client
        devis.finition_conditionnement = finition
        devis.commercial = client.commercial
        devis.statut = "nouveau"
        devis.creation = timezone.now()
        # Save devis to get an ID (required for many-to-many)
        devis.save()
        messages.success(self.request, "Votre demande de devis a été soumise avec succès.")
        envoyer_email_notification(
            "Nouveau devis reçu",
            f"Un nouveau devis a été soumis par {devis.client.nom_entreprise}.",
            [devis.client.commercial.user.email]
        )
        return redirect('client_dashboard')
    
@login_required
def modifier_devis(request, devis_id):
    devis = get_object_or_404(DevisNouveauProduit, pk=devis_id)

    if request.method == 'POST':
        devis_form = DevisForm(request.POST, request.FILES, instance=devis)
        finition = getattr(devis, 'finition_conditionnement', None)
        if finition:
            finition_form = FinitionConditionnementForm(request.POST, instance=finition)
        else:
            finition_form = FinitionConditionnementForm(request.POST)

        if devis_form.is_valid() and finition_form.is_valid():
            devis_form.save()

            finition_obj = finition_form.save(commit=False)
            finition_obj.devis = devis
            finition_obj.save()

            messages.success(request, "Devis modifié avec succès.")
            return redirect('traiter_devis', devis_id=devis.pk)

    else:
        devis_form = DevisForm(instance=devis)
        finition = getattr(devis, 'finition_conditionnement', None)
        finition_form = FinitionConditionnementForm(instance=finition)

    return render(request, 'devis/modifier_devis.html', {
        'devis_form': devis_form,
        'finition_form': finition_form,
        'devis': devis
    })


@login_required
def devis_par_client(request):
    try:
        commercial = Commercial.objects.get(user=request.user)
    except Commercial.DoesNotExist:
        return HttpResponseForbidden("Vous n'êtes pas un commercial.")

    clients = Client.objects.filter(commercial=commercial)

    devis_list = DevisNouveauProduit.objects.select_related('client').filter(
        client__in=clients,
        statut__in=["nouveau", "en_traitement"]
    ).order_by('-date_creation')

    context = {
        'devis_list': devis_list  
    }
    return render(request, 'devis/devis_non_lus.html', context)

@login_required
def devis_complet(request):
    try:
        commercial = Commercial.objects.get(user=request.user)
    except Commercial.DoesNotExist:
        return HttpResponseForbidden("Vous n'êtes pas un commercial.")

    clients = Client.objects.filter(commercial=commercial)

    devis_list = DevisNouveauProduit.objects.select_related('client').filter(
        client__in=clients,
        statut="complet"
    ).order_by('-traitement_date')

    context = {
        'devis_list': devis_list  
    }
    return render(request, 'devis/retour_be.html', context)

@login_required
def traiter_devis(request, devis_id):
    devis = get_object_or_404(DevisNouveauProduit, pk=devis_id)
    support_formset = SupportFormSet(request.POST)
    if request.method == 'POST':
        action = request.POST.get("action")
        if action == "soumettre":
            if support_formset.is_valid():
                for form in support_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        support = form.save(commit=False)
                        support.devis = devis
                        support.save()
                        devis.statut='envoye_be'
                        devis.save()
                for form in support_formset.deleted_forms:
                    if form.instance.pk:
                        form.instance.delete()
                be=BE.objects.get(pk=1)
                envoyer_email_notification(
                    "Nouveau devis reçu",
                    f"Un nouveau devis a été soumis par {devis.client.nom_entreprise}.",
                    [be.user.email]
                )
                messages.success(request,"Demande de devis soumis au BE")
                return redirect('commercial_dashboard')
        elif action == "modifier":
            devis.update_date = timezone.now()
            devis.statut = "en_traitement"
            devis.save()
            return redirect('modifier_devis', devis_id=devis.pk)

        elif action == "retour":
            devis.update_date = timezone.now()
            devis.statut = "en_traitement"
            devis.save()
            return redirect('devis_par_client')
    else:
        support_formset = SupportFormSet(queryset=Support.objects.none())
    return render(request, 'devis/traiter_devis.html', {
        'devis': devis,
        'support_formset': support_formset
    })

@login_required
def traiter_devis_be(request, devis_id):
    devis = get_object_or_404(DevisNouveauProduit, pk=devis_id)
    supports = Support.objects.filter(devis=devis)
    if request.method == 'POST':
        form = BEDevisForm(request.POST)
        coloration_formset = ColorationFormSet(request.POST,prefix='coloration')
        outillage_formset = OutillageFormSet(request.POST, prefix='outillage')
        cotation_formset = CotationFormSet(request.POST, prefix='cotation')

        if 'soumettre' in request.POST:
            if form.is_valid():
                analyse = form.save()
                for cform in coloration_formset:
                    if cform.is_valid():
                        coloration = cform.save(commit=False)
                        coloration.analyseTech = analyse
                        coloration.save()

                for oform in outillage_formset:
                    if oform.is_valid():
                        outillage = oform.save(commit=False)
                        outillage.analyse = analyse
                        outillage.save()

                for coform in cotation_formset:
                    if coform.is_valid():
                        cotation = coform.save(commit=False)
                        cotation.analyseBe = analyse
                        cotation.save()

                context = {
                    'devis': devis, 
                    'supports': devis.supports.all(),  
                    'analyse': devis.analyseBE,
                    'colorations': devis.analyseBE.coloration_set.all() if devis.analyseBE else [],
                    'outillages': devis.analyseBE.outillage_set.all() if devis.analyseBE else [],
                    'cotation': devis.analyseBE.cotation_set.all() if devis.analyseBE else [],
                }
                html = render_to_string('devis/devis_template.html', context)
                result = BytesIO()
                pdf_status = pisa.CreatePDF(html, dest=result)

                if not pdf_status.err:
                    pdf_file = ContentFile(result.getvalue(), name=f'devis_{timezone.now().strftime("%Y%m%d%H%M%S")}.pdf')
                    generated_doc = GeneratedDoc.objects.create(
                        generated_by= request.user,
                        doc=pdf_file,
                        type_doc='devis',
                        date_creation=timezone.now(),
                    )
                devis.generated_doc = generated_doc
                devis.traitement_date=timezone.now()
                devis.statut='complet'
                devis.analyseBE=analyse
                devis.save()
                envoyer_email_notification(
                    "Nouveau devis reçu",
                    f"Un nouveau devis a été soumis par le BE.",
                    [devis.client.commercial.user.email]
                )
                messages.success(request,"Le devis a été soumis avec succès")
                return redirect('be_dashboard')
        elif 'retour' in request.POST:
            devis.statut = 'en_traitement_be'
            devis.save()
            return redirect('be_dashboard')

    else:
        form = BEDevisForm()
        coloration_formset = ColorationFormSet(prefix='coloration')
        outillage_formset = OutillageFormSet(prefix='outillage')
        cotation_formset = CotationFormSet(prefix='cotation')


    return render(request, 'devis/traiter_devis_be.html', {
        'devis': devis,
        'supports': supports,
        'form': form,
        'coloration_formset': coloration_formset,
        'outillage_formset': outillage_formset,
        'cotation_formset': cotation_formset,
    })

@login_required
def detail_devis(request, devis_id):
    devis = get_object_or_404(DevisNouveauProduit, pk=devis_id)

    if request.user != devis.client.commercial.user:
        return HttpResponseForbidden("Accès refusé.")

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'creer_proforma':
            return redirect('creer_proforma', devis_id=devis.id)
        elif action == 'retour':
            devis.statut = 'complet'
            devis.save()
            messages.info(request, "Le devis a été marqué comme en traitement.")
            return redirect('devis_complet')

    return render(request, 'devis/detail_devis.html', {
        'devis': devis
    })

