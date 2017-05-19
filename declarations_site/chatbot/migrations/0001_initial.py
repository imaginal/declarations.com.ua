# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-19 23:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_id', models.CharField(max_length=250, verbose_name='FromID')),
                ('from_name', models.CharField(max_length=250, verbose_name='FromName')),
                ('conversation', models.CharField(max_length=250, verbose_name='Conversation')),
                ('query', models.CharField(max_length=250, verbose_name='Запит')),
                ('answer', models.CharField(max_length=250, verbose_name='Відповідь')),
                ('timestamp', models.CharField(max_length=50, verbose_name='Timestamp')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Створений')),
                ('user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
