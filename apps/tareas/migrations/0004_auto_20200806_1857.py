# Generated by Django 3.0.9 on 2020-08-06 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0003_auto_20200727_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='asignartarea',
            name='justificacion',
            field=models.CharField(default='sin justificar', max_length=50),
        ),
        migrations.AddField(
            model_name='asignartarea',
            name='notica_objetar',
            field=models.BooleanField(default=False),
        ),
    ]
