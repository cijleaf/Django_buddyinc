# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0019_auto_20171023_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='access_token',
            field=models.CharField(max_length=200, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='account_status',
            field=models.CharField(max_length=100, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='dwolla_PIN',
            field=models.CharField(max_length=50, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='dwolla_account_id',
            field=models.CharField(max_length=200, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='funding_id',
            field=models.CharField(max_length=200, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='funding_source_name',
            field=models.CharField(max_length=200, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='load_zone',
            field=models.CharField(max_length=100, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='meter_number',
            field=models.CharField(max_length=200, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='phone',
            field=models.CharField(max_length=100, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='refresh_token',
            field=models.CharField(max_length=200, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='utility_api_uid',
            field=models.CharField(max_length=20, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='utility_meter_uid',
            field=models.CharField(max_length=20, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='utility_provider',
            field=models.CharField(max_length=100, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='utility_service_identifier',
            field=models.CharField(max_length=50, blank=True, default=''),
            preserve_default=False,
        ),
    ]
