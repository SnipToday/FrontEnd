# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-25 21:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('snips', '0015_snip_comments_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Referer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('referer', models.CharField(max_length=100)),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sessions.Session')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SessionToUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sessions.Session')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SnipLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'login'), ('readmore', 'readmore'), ('like', 'like'), ('dislike', 'dislike'), ('share', 'share'), ('viewed', 'viewed'), ('locked', 'locked'), ('open_link', 'open_link')], max_length=15, verbose_name='action')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('param1', models.CharField(blank=True, max_length=20, null=True)),
                ('param2', models.CharField(blank=True, max_length=20, null=True)),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sessions.Session')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.RemoveField(
            model_name='anonlog',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userlog',
            name='user',
        ),
        migrations.DeleteModel(
            name='AnonLog',
        ),
        migrations.DeleteModel(
            name='UserLog',
        ),
    ]
