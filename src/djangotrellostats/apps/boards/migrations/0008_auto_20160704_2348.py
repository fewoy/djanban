# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-04 23:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0007_card_labels'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='cycle_time',
            field=models.DecimalField(decimal_places=4, default=None, max_digits=12, null=True, verbose_name='Lead time'),
        ),
        migrations.AddField(
            model_name='card',
            name='lead_time',
            field=models.DecimalField(decimal_places=4, default=None, max_digits=12, null=True, verbose_name='Cycle time'),
        ),
    ]
