# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-26 15:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work_hours_packages', '0002_auto_20170526_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='workhourspackage',
            name='notification_email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='Notification email when number of hours is reached'),
        ),
    ]
