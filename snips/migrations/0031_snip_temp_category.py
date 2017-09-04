# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-08 09:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('snips', '0030_tempcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='snip',
            name='temp_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='snips.TempCategory'),
        ),
    ]