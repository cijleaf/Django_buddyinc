# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0031_auto_20180813_1943'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contract',
            options={'ordering': ('-created_on',)},
        ),
        migrations.AlterModelOptions(
            name='installation',
            options={'ordering': ('-created_on',)},
        ),
        migrations.AlterField(
            model_name='deal',
            name='docusign_contract',
            field=models.FileField(max_length=512, null=True, upload_to='', blank=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='docusign_envelope_id',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
