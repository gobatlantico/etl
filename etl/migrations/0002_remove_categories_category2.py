# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-06 13:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('etl', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categories',
            name='category2',
        ),
    ]
