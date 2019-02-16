# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0034_auto_20180907_0256'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('ip_address', models.CharField(max_length=32, null=True)),
                ('action', models.CharField(max_length=50)),
                ('funding_name', models.CharField(max_length=100, null=True)),
                ('funding_id', models.IntegerField(null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SellerBusinessInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('business_name', models.CharField(max_length=256)),
                ('business_type', models.CharField(max_length=64, choices=[('corporation', 'corporation'), ('llc', 'llc'), ('partnership', 'partnership')])),
                ('business_classification', models.CharField(max_length=256)),
                ('ein', models.CharField(max_length=256)),
                ('controller_first_name', models.CharField(max_length=256)),
                ('controller_last_name', models.CharField(max_length=256)),
                ('controller_job_title', models.CharField(max_length=256)),
                ('controller_date_of_birth', models.DateField()),
                ('controller_ssn', models.CharField(max_length=256)),
                ('controller_address', models.CharField(max_length=256)),
                ('controller_city', models.CharField(max_length=128)),
                ('controller_state', models.CharField(max_length=2)),
                ('controller_country', models.CharField(max_length=2)),
                ('seller', models.ForeignKey(related_name='business_information_seller', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
    ]
