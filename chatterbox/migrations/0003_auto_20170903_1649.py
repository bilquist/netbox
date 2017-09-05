# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-03 23:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatterbox', '0002_auto_20170903_1621'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ldaviewparameters',
            name='id',
        ),
        migrations.AlterField(
            model_name='ldaviewparameters',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]