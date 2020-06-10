# Generated by Django 3.0.6 on 2020-05-31 19:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hogar', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tarea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('complejidad', models.PositiveIntegerField(default=0)),
                ('duracion', models.IntegerField(default=0)),
                ('lugar', models.CharField(max_length=50)),
                ('fecha_creacion', models.DateField(auto_now_add=True)),
                ('comentarios', models.TextField(blank=True, max_length=200)),
                ('completada', models.BooleanField(default=False)),
                ('domicilio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hogar.Domicilio')),
            ],
        ),
    ]