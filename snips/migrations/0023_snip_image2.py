# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-30 13:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
        ('snips', '0022_auto_20170430_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='snip',
            name='image2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.SnipImage'),
        ),
    ]
