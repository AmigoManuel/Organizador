# Generated by Django 3.0.5 on 2020-06-24 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('almanac_calendar', '0005_auto_20200624_1536'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='description',
        ),
    ]