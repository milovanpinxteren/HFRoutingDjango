# Generated by Django 5.0.4 on 2024-05-07 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HFRoutingApp', '0011_rename_routes_route'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='fill_time_minutes',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
