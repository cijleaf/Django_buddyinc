# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0003_auto_20160804_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='docusign_contract',
            field=models.FileField(null=True, upload_to='', max_length=512),
        ),
        migrations.AddField(
            model_name='deal',
            name='docusign_envelope_id',
            field=models.CharField(null=True, max_length=128),
        ),
    ]
