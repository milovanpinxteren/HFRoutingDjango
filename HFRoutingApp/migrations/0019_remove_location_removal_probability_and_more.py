# Generated by Django 5.0.4 on 2024-05-08 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HFRoutingApp', '0018_alter_weekday_day'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='removal_probability',
        ),
        migrations.RemoveField(
            model_name='machine',
            name='avg_no_crates',
        ),
        migrations.RemoveField(
            model_name='machine',
            name='fill_dates',
        ),
        migrations.RemoveField(
            model_name='machine',
            name='fill_time_minutes',
        ),
        migrations.RemoveField(
            model_name='machine',
            name='walking_time_minutes',
        ),
        migrations.AddField(
            model_name='spot',
            name='avg_no_crates',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='spot',
            name='fill_dates',
            field=models.ManyToManyField(blank=True, to='HFRoutingApp.weekday'),
        ),
        migrations.AddField(
            model_name='spot',
            name='fill_time_minutes',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='spot',
            name='removal_probability',
            field=models.FloatField(blank=True, null=True, verbose_name='removal probability'),
        ),
        migrations.AddField(
            model_name='spot',
            name='walking_time_minutes',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
