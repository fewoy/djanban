# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-03 20:30
from __future__ import unicode_literals

from django.db import migrations, models


def set_number_of_rewiews(apps, schema):
    Card = apps.get_model("boards", "Card")
    for card in Card.objects.all():
        card.number_of_reviews = card.reviews.all().count()
        card.save()


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0051_auto_20170303_2050'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='number_of_reviews',
            field=models.PositiveIntegerField(default=0, verbose_name='Number of reviews of this card'),
        ),
        migrations.RunPython(set_number_of_rewiews)
    ]