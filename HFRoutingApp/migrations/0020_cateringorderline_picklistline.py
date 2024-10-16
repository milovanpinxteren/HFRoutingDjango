# Generated by Django 5.0.4 on 2024-05-08 12:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HFRoutingApp', '0019_remove_location_removal_probability_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CateringOrderLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('catering_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HFRoutingApp.cateringorder')),
            ],
        ),
        migrations.CreateModel(
            name='PickListLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distr_date', models.DateField()),
                ('quantity', models.IntegerField(default=0)),
                ('spot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HFRoutingApp.spot')),
            ],
        ),
    ]
