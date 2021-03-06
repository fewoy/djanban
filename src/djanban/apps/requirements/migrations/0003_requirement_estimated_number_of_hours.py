# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-19 16:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requirements', '0002_requirement_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='requirement',
            name='estimated_number_of_hours',
            field=models.PositiveIntegerField(blank=True, default=None, help_text='Number of hours in the budget', null=True, verbose_name='Estimated number of hours to be completed'),
        ),
    ]
