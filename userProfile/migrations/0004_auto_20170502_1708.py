# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-02 14:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0003_sessiontouser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessiontouser',
            name='session',
            field=models.CharField(max_length=32),
        ),
    ]
