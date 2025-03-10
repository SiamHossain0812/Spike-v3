# Generated by Django 5.1.6 on 2025-02-09 07:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RiverTypeThreshold',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('river_type', models.CharField(max_length=50, unique=True)),
                ('threshold_value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='StationName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='StationRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_id', models.CharField(max_length=50)),
                ('recorded_highest_wl', models.FloatField()),
                ('recorded_lowest_wl', models.FloatField()),
                ('river_type', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpikeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateTime', models.CharField(max_length=100)),
                ('value', models.FloatField(blank=True, null=True)),
                ('modified_value', models.FloatField(blank=True, null=True)),
                ('station_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='uiApp.stationname')),
            ],
        ),
    ]
