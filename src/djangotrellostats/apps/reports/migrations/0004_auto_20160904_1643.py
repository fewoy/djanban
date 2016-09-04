# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-04 14:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_auto_20160903_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardmovement',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='card_movements', to='boards.Board', verbose_name='Board'),
        ),
    ]
