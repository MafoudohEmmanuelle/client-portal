# Generated by Django 5.2.1 on 2025-05-20 19:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        ('proforma', '0004_alter_proforma_statut'),
    ]

    operations = [
        migrations.AddField(
            model_name='proforma',
            name='generated_doc',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='documents.generateddoc'),
        ),
    ]
