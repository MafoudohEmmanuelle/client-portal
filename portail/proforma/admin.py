from django.contrib import admin
from .models import Produit,Proforma,ProduitQuote,ProduitQuoteItem,CoordonneeBancaire

admin.site.register(Proforma)
admin.site.register(Produit)
admin.site.register(ProduitQuote)
admin.site.register(ProduitQuoteItem)
admin.site.register(CoordonneeBancaire)