# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-18 08:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensors',
            name='label',
            field=models.CharField(max_length=28),
        ),
    ]
