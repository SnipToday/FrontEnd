# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-21 06:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('snips', '0005_auto_20170420_2108'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'login'), ('read_more', 'read_more'), ('like', 'like'), ('dislike', 'dislike'), ('share', 'share'), ('skip', 'skip')], max_length=15, verbose_name='action')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sessions.Session')),
            ],
            options={
                'verbose_name': 'Action log',
                'ordering': ['-date'],
                'verbose_name_plural': 'Actions log',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'login'), ('read_more', 'read_more'), ('like', 'like'), ('dislike', 'dislike'), ('share', 'share'), ('skip', 'skip')], max_length=15, verbose_name='action')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Action log',
                'ordering': ['-date'],
                'verbose_name_plural': 'Actions log',
                'abstract': False,
            },
        ),
    ]
