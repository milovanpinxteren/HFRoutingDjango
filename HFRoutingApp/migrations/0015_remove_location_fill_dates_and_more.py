# Generated by Django 5.0.4 on 2024-05-08 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HFRoutingApp', '0014_remove_location_fill_time_minutes_route_hub_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='fill_dates',
        ),
        migrations.RemoveField(
            model_name='spot',
            name='fill_time_minutes',
        ),
        migrations.RemoveField(
            model_name='spot',
            name='walking_time_minutes',
        ),
        migrations.AddField(
            model_name='machine',
            name='avg_no_crates',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='machine',
            name='fill_dates',
            field=models.ManyToManyField(blank=True, to='HFRoutingApp.weekday'),
        ),
        migrations.AddField(
            model_name='machine',
            name='fill_time_minutes',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='machine',
            name='walking_time_minutes',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
