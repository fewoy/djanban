# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-11 18:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0037_board_title_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='estimated_time',
        ),
        migrations.RemoveField(
            model_name='card',
            name='spent_time',
        ),
        migrations.AlterField(
            model_name='cardcomment',
            name='card',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='boards.Card', verbose_name='Card this comment belongs to'),
        ),
    ]
