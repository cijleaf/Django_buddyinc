# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0045_auto_20181004_1740'),
    ]

    operations = [
        migrations.CreateModel(
            name='BeneficialOwner',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('beneficial_first_name', models.CharField(max_length=256)),
                ('beneficial_last_name', models.CharField(max_length=256)),
                ('beneficial_date_of_birth', models.DateField()),
                ('beneficial_ssn', models.CharField(max_length=256)),
                ('beneficial_address', models.CharField(max_length=256)),
                ('beneficial_city', models.CharField(max_length=128)),
                ('beneficial_state', models.CharField(max_length=2)),
                ('beneficial_zip_code', models.CharField(max_length=20)),
                ('beneficial_country', models.CharField(max_length=2)),
                ('beneficial_owner_id', models.CharField(blank=True, null=True, max_length=256)),
                ('beneficial_status', models.CharField(blank=True, null=True, max_length=50)),
                ('certification_status', models.CharField(blank=True, null=True, max_length=50)),
                ('seller', models.ForeignKey(related_name='beneficial_owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
    ]
