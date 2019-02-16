# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0033_auto_20180815_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebhookLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('webhook_id', models.CharField(max_length=256)),
                ('resource_id', models.CharField(max_length=256)),
                ('topic', models.CharField(max_length=256)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='account',
            name='wepay_access_token',
        ),
        migrations.RemoveField(
            model_name='account',
            name='wepay_account_id',
        ),
        migrations.RemoveField(
            model_name='account',
            name='wepay_bank_last_four',
        ),
        migrations.RemoveField(
            model_name='account',
            name='wepay_bank_name',
        ),
        migrations.RemoveField(
            model_name='account',
            name='wepay_bank_state',
        ),
        migrations.RemoveField(
            model_name='account',
            name='wepay_payment_bank_id',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='wepay_transaction_id',
        ),
    ]
