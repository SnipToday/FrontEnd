# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-23 13:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snips', '0037_auto_20170519_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='display_name',
            field=models.CharField(default='topic', max_length=60),
            preserve_default=False,
        ),
    ]