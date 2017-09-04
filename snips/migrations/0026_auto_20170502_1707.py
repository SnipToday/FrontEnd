# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-02 14:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snips', '0025_auto_20170502_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsniplog',
            name='session',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='referer',
            name='session',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='sniplog',
            name='session',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True),
        ),
    ]