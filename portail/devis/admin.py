from django.contrib import admin
from .models import DevisNouveauProduit, FinitionConditionnement,Categorie,Support,Cotation, Coloration, AnalyseTechniqueBE,Outillage

admin.site.register(DevisNouveauProduit)
admin.site.register(FinitionConditionnement)
admin.site.register(Categorie)
admin.site.register(Support)
admin.site.register(AnalyseTechniqueBE)
admin.site.register(Coloration)
admin.site.register(Outillage)
admin.site.register(Cotation)

