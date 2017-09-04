# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-22 17:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('snips', '0009_auto_20170421_1918'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.CharField(choices=[('like', 'like'), ('dislike', 'dislike')], max_length=10)),
                ('date', models.DateTimeField()),
                ('snip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snips.Snip')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]