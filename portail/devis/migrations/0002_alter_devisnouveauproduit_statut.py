# Generated by Django 5.2.1 on 2025-05-19 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devis', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devisnouveauproduit',
            name='statut',
            field=models.CharField(choices=[('nouveau', 'Nouveau'), ('en_traitement', 'En traitement'), ('envoye_be', 'Nouveau Devis'), ('en_traitement_be', 'En cour de traitement'), ('complet', 'Devis Complet'), ('finalise', 'Finaliséé')], default='nouveau', max_length=30),
        ),
    ]
