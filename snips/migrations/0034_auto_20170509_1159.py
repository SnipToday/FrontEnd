# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-09 08:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snips', '0033_auto_20170508_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsniplog',
            name='action',
            field=models.CharField(choices=[('readmore', 'readmore'), ('like', 'like'), ('dislike', 'dislike'), ('share', 'share'), ('viewed', 'viewed'), ('locked', 'locked'), ('open_link', 'open_link'), ('reach_limit', 'reach_limit'), ('like_noauth', 'like_noauth'), ('dislike_noauth', 'dislike_noauth')], max_length=20, verbose_name='action'),
        ),
        migrations.AlterField(
            model_name='sniplog',
            name='action',
            field=models.CharField(choices=[('readmore', 'readmore'), ('like', 'like'), ('dislike', 'dislike'), ('share', 'share'), ('viewed', 'viewed'), ('locked', 'locked'), ('open_link', 'open_link'), ('reach_limit', 'reach_limit'), ('like_noauth', 'like_noauth'), ('dislike_noauth', 'dislike_noauth')], max_length=20, verbose_name='action'),
        ),
    ]
