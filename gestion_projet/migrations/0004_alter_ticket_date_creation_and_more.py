# Generated by Django 5.0.7 on 2024-08-01 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_projet', '0003_ticket_date_creation_ticket_membre_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='date_creation',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='moment_creation',
            field=models.TimeField(auto_now_add=True),
        ),
    ]
