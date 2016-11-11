# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-11 18:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dev_times', '0006_auto_20161012_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyspenttime',
            name='comment',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='daily_spent_time', to='boards.CardComment', verbose_name='Comment'),
        ),
        migrations.AlterField(
            model_name='dailyspenttime',
            name='uuid',
            field=models.CharField(max_length=128, null=True, verbose_name='External id of the comment'),
        ),
    ]
