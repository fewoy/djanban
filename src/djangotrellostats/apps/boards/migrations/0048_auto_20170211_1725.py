# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-11 16:25
from __future__ import unicode_literals

from django.db import migrations, models


def update_movement_count(apps, schema_editor):
    Card = apps.get_model("boards", "Card")
    for card in Card.objects.all():
        card.number_of_forward_movements = card.movements.filter(type="forward").count()
        card.number_of_backward_movements = card.movements.filter(type="backward").count()
        card.save()


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0047_auto_20170211_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='number_of_backward_movements',
            field=models.PositiveIntegerField(default=0, verbose_name='Number of backward movements'),
        ),
        migrations.AddField(
            model_name='card',
            name='number_of_forward_movements',
            field=models.PositiveIntegerField(default=0, verbose_name='Number of forward movements'),
        ),
        migrations.RunPython(update_movement_count)
    ]