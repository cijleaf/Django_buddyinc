# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0038_remove_transaction_seller_bill_amount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deal',
            options={'ordering': ('-created_on',)},
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ('-created_on',)},
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(max_length=32, db_index=True, blank=True, null=True),
        ),
        migrations.CreateModel(
            name='VerificationDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('document_type', models.CharField(max_length=64, choices=[('passport', 'passport'), ('license', 'license'), ('idCard', 'idCard'), ('other', 'other')])),
                ('document_id', models.CharField(max_length=256)),
                ('user', models.ForeignKey(related_name='verification_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
    ]
