# Generated by Django 5.1.6 on 2025-02-09 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uiApp', '0002_rename_modified_value_spikedata_spike_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spikedata',
            name='station_name',
        ),
    ]
