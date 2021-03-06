# Generated by Django 3.0.7 on 2020-07-05 18:49

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dependencia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Domicilio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calle', models.CharField(max_length=50)),
                ('numero', models.IntegerField(default=0)),
                ('comuna', models.CharField(max_length=50)),
                ('ciudad', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('es_administrador', models.BooleanField(default=True)),
                ('telefono', models.CharField(max_length=50)),
                ('domicilio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hogar.Domicilio')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='PerteneceDependencia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asignada', models.BooleanField(default=False)),
                ('dependencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hogar.Dependencia')),
                ('domicilio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hogar.Domicilio')),
            ],
        ),
    ]
