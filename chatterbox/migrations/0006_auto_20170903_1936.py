# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-04 02:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatterbox', '0005_auto_20170903_1931'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ldaviewparameters',
            old_name='bool_use_cached_model',
            new_name='use_cached_model',
        ),
    ]