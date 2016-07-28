# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-24 21:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0006_board_hourly_rates'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='backward_movements',
            field=models.PositiveIntegerField(default=0, verbose_name='Backward movements of this card'),
        ),
        migrations.AddField(
            model_name='card',
            name='forward_movements',
            field=models.PositiveIntegerField(default=0, verbose_name='Forward movements of this card'),
        ),
        migrations.AddField(
            model_name='card',
            name='time',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=12, verbose_name='Time this card is alive in the board'),
        ),
    ]