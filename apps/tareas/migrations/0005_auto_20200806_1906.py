# Generated by Django 3.0.9 on 2020-08-06 19:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0004_auto_20200806_1857'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asignartarea',
            old_name='notica_objetar',
            new_name='notifica_objetar',
        ),
    ]
