# Generated by Django 5.0.7 on 2024-10-17 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_projet', '0016_delete_food'),
    ]

    operations = [
        migrations.CreateModel(
            name='food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('ingredient1', models.TextField()),
                ('ingredient2', models.TextField()),
                ('ingredient3', models.TextField()),
                ('ingredient4', models.TextField()),
                ('duration', models.TimeField()),
            ],
        ),
    ]
