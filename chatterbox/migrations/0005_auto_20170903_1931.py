# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-04 02:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatterbox', '0004_auto_20170903_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='ldaviewparameters',
            name='bool_use_cached_model',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ldaviewparameters',
            name='num_passes',
            field=models.PositiveSmallIntegerField(default=20),
        ),
        migrations.AddField(
            model_name='ldaviewparameters',
            name='num_topics',
            field=models.PositiveSmallIntegerField(default=5),
        ),
        migrations.AddField(
            model_name='ldaviewparameters',
            name='num_words',
            field=models.PositiveSmallIntegerField(default=3),
        ),
    ]
