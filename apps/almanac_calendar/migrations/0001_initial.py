# Generated by Django 3.0.5 on 2020-06-21 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, choices=[('EV', 'Event'), ('HD', 'Holiday'), ('EX', 'Exam')], default='EV', max_length=10, null=True)),
                ('title', models.CharField(default='Title', max_length=100)),
                ('start', models.DateField()),
                ('end', models.DateField()),
            ],
        ),
    ]
