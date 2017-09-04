# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-02 16:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0005_userlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlog',
            name='action',
            field=models.CharField(choices=[('signin', 'signin'), ('signup', 'signup'), ('subscribe', 'subscribe')], max_length=15, verbose_name='action'),
        ),
    ]
