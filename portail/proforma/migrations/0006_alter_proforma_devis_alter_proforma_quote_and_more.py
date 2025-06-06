# Generated by Django 5.2.1 on 2025-05-26 10:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devis', '0003_alter_finitionconditionnement_contenant_and_more'),
        ('proforma', '0005_proforma_generated_doc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proforma',
            name='devis',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='proformas', to='devis.devisnouveauproduit'),
        ),
        migrations.AlterField(
            model_name='proforma',
            name='quote',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='proformas', to='proforma.produitquote'),
        ),
        migrations.AlterField(
            model_name='proformaitem',
            name='produit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='proforma.produit'),
        ),
    ]
