# Generated by Django 5.0.7 on 2024-08-01 18:09

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_projet', '0005_alter_ticket_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='description',
            field=tinymce.models.HTMLField(),
        ),
    ]
