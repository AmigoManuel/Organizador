# Generated by Django 3.0.7 on 2020-06-19 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0002_auto_20200531_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarea',
            name='duracion',
            field=models.DurationField(default=0),
        ),
    ]