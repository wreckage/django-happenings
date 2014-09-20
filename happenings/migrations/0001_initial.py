# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cancellation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reason', models.CharField(max_length=255, verbose_name='reason')),
                ('date', models.DateField(verbose_name='date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(verbose_name='start date')),
                ('end_date', models.DateTimeField(verbose_name='end date')),
                ('all_day', models.BooleanField(default=False, verbose_name='all day')),
                ('repeat', models.CharField(default='NEVER', max_length=15, verbose_name='repeat', choices=[('NEVER', 'Never'), ('DAILY', 'Every Day'), ('WEEKDAY', 'Every Weekday'), ('WEEKLY', 'Every Week'), ('BIWEEKLY', 'Every 2 Weeks'), ('MONTHLY', 'Every Month'), ('YEARLY', 'Every Year')])),
                ('end_repeat', models.DateField(null=True, verbose_name='end repeat', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('description', models.TextField(verbose_name='description')),
                ('background_color', models.CharField(default='eeeeee', max_length=10, verbose_name='background color', choices=[('eeeeee', 'gray'), ('ff0000', 'red'), ('0000ff', 'blue'), ('00ff00', 'green'), ('000000', 'black'), ('ffffff', 'white')])),
                ('background_color_custom', models.CharField(help_text='Must be a valid hex triplet. Default is gray (eeeeee)', max_length=6, verbose_name='background color custom', blank=True)),
                ('font_color', models.CharField(default='000000', max_length=10, verbose_name='font color', choices=[('eeeeee', 'gray'), ('ff0000', 'red'), ('0000ff', 'blue'), ('00ff00', 'green'), ('000000', 'black'), ('ffffff', 'white')])),
                ('font_color_custom', models.CharField(help_text='Must be a valid hex triplet. Default is black (000000)', max_length=6, verbose_name='font color custom', blank=True)),
                ('categories', models.ManyToManyField(to='happenings.Category', verbose_name='categories', blank=True)),
                ('created_by', models.ForeignKey(related_name='events', verbose_name='created by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('address_line_1', models.CharField(max_length=255, verbose_name='Address Line 1', blank=True)),
                ('address_line_2', models.CharField(max_length=255, verbose_name='Address Line 2', blank=True)),
                ('address_line_3', models.CharField(max_length=255, verbose_name='Address Line 3', blank=True)),
                ('state', models.CharField(max_length=63, verbose_name='State / Province / Region', blank=True)),
                ('city', models.CharField(max_length=63, verbose_name='City / Town', blank=True)),
                ('zipcode', models.CharField(max_length=31, verbose_name='ZIP / Postal Code', blank=True)),
                ('country', models.CharField(max_length=127, verbose_name='Country', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.ManyToManyField(to='happenings.Location', verbose_name='locations', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(to='happenings.Tag', verbose_name='tags', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cancellation',
            name='event',
            field=models.ForeignKey(related_query_name='cancellation', related_name='cancellations', to='happenings.Event'),
            preserve_default=True,
        ),
    ]
