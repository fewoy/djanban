# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-07 18:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0009_auto_20160707_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowcardreport',
            name='workflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='workflow_card_reports', to='boards.Workflow', verbose_name='Workflow'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workflowcardreport',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workflow_card_reports', to='boards.Board', verbose_name='Board'),
        ),
        migrations.AlterField(
            model_name='workflowcardreport',
            name='card',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workflow_card_reports', to='boards.Card', verbose_name='Card'),
        ),
        migrations.AlterField(
            model_name='workflowcardreport',
            name='fetch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workflow_card_reports', to='boards.Fetch', verbose_name='Fetch'),
        ),
    ]
