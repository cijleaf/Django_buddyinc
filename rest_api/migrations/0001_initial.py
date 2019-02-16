# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(blank=True, verbose_name='last login', null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(unique=True, max_length=256)),
                ('role', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=128)),
                ('phone', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(max_length=256)),
                ('city', models.CharField(max_length=128)),
                ('state', models.CharField(max_length=2)),
                ('zip_code', models.CharField(max_length=100)),
                ('connect_preference', models.CharField(max_length=32, default='email')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('verified_at', models.DateTimeField(null=True)),
                ('credit_to_sell_percent', models.IntegerField(blank=True, null=True)),
                ('credit_to_sell', models.FloatField(blank=True, null=True, default=0)),
                ('credit_to_buy', models.FloatField(blank=True, null=True, default=0)),
                ('remaining_credit', models.FloatField(default=0)),
                ('load_zone', models.CharField(blank=True, max_length=100, null=True)),
                ('utility_provider', models.CharField(blank=True, max_length=100, null=True)),
                ('utility_api_user_uid', models.CharField(blank=True, max_length=20, null=True)),
                ('utility_api_uid', models.CharField(blank=True, max_length=20, null=True)),
                ('utility_service_id', models.CharField(blank=True, max_length=50, null=True)),
                ('meter_number', models.CharField(blank=True, max_length=200, null=True)),
                ('account_number', models.CharField(blank=True, max_length=200, null=True)),
                ('dwolla_account_id', models.CharField(blank=True, max_length=200, null=True)),
                ('refresh_token', models.CharField(blank=True, max_length=200, null=True)),
                ('access_token', models.CharField(blank=True, max_length=200, null=True)),
                ('account_status', models.CharField(blank=True, max_length=100, null=True)),
                ('funding_id', models.CharField(blank=True, max_length=200, null=True)),
                ('funding_source_name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('quantity', models.BigIntegerField()),
                ('demand_date', models.DateField()),
                ('transaction_date', models.DateField()),
                ('status', models.CharField(max_length=32, default='pending_seller')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('buyer', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='deals_buyer')),
                ('seller', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='deals_seller')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('bill_statement_date', models.DateField()),
                ('actual_amount', models.FloatField()),
                ('fee', models.FloatField(blank=True, null=True)),
                ('paid_to_seller', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(max_length=32)),
                ('dwolla_transaction_id', models.CharField(blank=True, max_length=200, null=True)),
                ('deal', models.ForeignKey(to='rest_api.Deal', related_name='transactions')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='transaction',
            unique_together=set([('deal', 'bill_statement_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='deal',
            unique_together=set([('seller', 'buyer')]),
        ),
    ]
