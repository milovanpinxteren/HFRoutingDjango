# Generated by Django 5.0.4 on 2024-05-07 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HFRoutingApp', '0012_location_fill_time_minutes'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='opening_time',
            field=models.TimeField(blank=True, null=True, verbose_name='opening time'),
        ),
    ]
