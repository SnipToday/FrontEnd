# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-23 12:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snips', '0010_vote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anonlog',
            name='action',
            field=models.CharField(choices=[('login', 'login'), ('read_more', 'read_more'), ('like', 'like'), ('dislike', 'dislike'), ('share', 'share'), ('viewed', 'viewed'), ('locked', 'locked')], max_length=15, verbose_name='action'),
        ),
        migrations.AlterField(
            model_name='userlog',
            name='action',
            field=models.CharField(choices=[('login', 'login'), ('read_more', 'read_more'), ('like', 'like'), ('dislike', 'dislike'), ('share', 'share'), ('viewed', 'viewed'), ('locked', 'locked')], max_length=15, verbose_name='action'),
        ),
    ]