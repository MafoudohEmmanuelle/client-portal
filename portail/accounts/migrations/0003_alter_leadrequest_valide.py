# Generated by Django 5.2.1 on 2025-05-23 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_leadrequest_valide'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadrequest',
            name='valide',
            field=models.BooleanField(default=True),
        ),
    ]
