# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0020_auto_20171103_1639'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('contract_file', models.FileField(max_length=1024, null=True, upload_to='contracts/%Y/')),
                ('initials_file', models.FileField(max_length=1024, null=True, upload_to='contracts/%Y/')),
                ('deal', models.ForeignKey(related_name='contracts', on_delete=django.db.models.deletion.PROTECT, to='rest_api.Deal')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
