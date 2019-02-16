# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0012_auto_20170130_1756'),
    ]

    operations = [
        migrations.CreateModel(
            name='Installation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128)),
                ('address', models.CharField(max_length=256)),
                ('city', models.CharField(max_length=128)),
                ('state', models.CharField(max_length=2)),
                ('zip_code', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('average_monthly_credit', models.IntegerField(null=True, blank=True)),
                ('credit_to_sell_percent', models.IntegerField(default=0, blank=True)),
                ('credit_to_sell', models.FloatField(default=0, null=True, blank=True)),
                ('remaining_credit', models.FloatField(default=0)),
                ('load_zone', models.CharField(max_length=100, null=True, blank=True)),
                ('community_code', models.CharField(max_length=50, null=True, blank=True)),
                ('utility_provider', models.CharField(max_length=100, null=True, blank=True)),
                ('utility_api_uid', models.CharField(max_length=20, null=True, blank=True)),
                ('utility_meter_uid', models.CharField(max_length=20, null=True, blank=True)),
                ('utility_service_identifier', models.CharField(max_length=50, null=True, blank=True)),
                ('utility_activated', models.BooleanField(default=False)),
                ('account', models.ForeignKey(related_name='installation_account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
