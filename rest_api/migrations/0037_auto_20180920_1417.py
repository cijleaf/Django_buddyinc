# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0036_auto_20180918_0424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='access_token',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='account_status',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='dwolla_account_id',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='funding_id',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='funding_source_name',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='refresh_token',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
