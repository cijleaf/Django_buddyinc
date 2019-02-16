# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0014_auto_20170223_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='installation',
            field=models.ForeignKey(blank=True, to='rest_api.Installation', null=True, related_name='deals'),
        ),
    ]
