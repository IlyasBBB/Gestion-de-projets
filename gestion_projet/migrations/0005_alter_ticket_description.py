# Generated by Django 5.0.7 on 2024-08-01 18:01

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_projet', '0004_alter_ticket_date_creation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
