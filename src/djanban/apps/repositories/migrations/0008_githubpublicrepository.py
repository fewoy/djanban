# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-23 18:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repositories', '0007_commit_assessment_datetime'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitHubPublicRepository',
            fields=[
                ('repository_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='repositories.Repository')),
                ('username', models.CharField(max_length=128, verbose_name='Username')),
            ],
            options={
                'verbose_name': 'GitHub public repository',
                'verbose_name_plural': 'GitHub public repositories',
            },
            bases=('repositories.repository',),
        ),
    ]