# Generated by Django 3.0.7 on 2020-08-06 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hogar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='puntaje_obtenido',
            field=models.IntegerField(default=0),
        ),
    ]
