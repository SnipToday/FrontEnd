# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-04 11:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snips', '0028_auto_20170502_1938'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='snip',
            name='death_date',
        ),
        migrations.AddField(
            model_name='snip',
            name='death_days',
            field=models.IntegerField(default=30, verbose_name='Days to live'),
            preserve_default=False,
        ),
    ]
