# Generated by Django 5.2.1 on 2025-05-23 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_leadrequest_valide'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadrequest',
            name='converted',
            field=models.BooleanField(default=False),
        ),
    ]
