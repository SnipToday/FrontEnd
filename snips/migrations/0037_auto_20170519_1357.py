# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-19 10:57
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('snips', '0036_auto_20170517_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snip',
            name='body',
            field=wagtail.wagtailcore.fields.RichTextField(verbose_name='Body'),
        ),
    ]