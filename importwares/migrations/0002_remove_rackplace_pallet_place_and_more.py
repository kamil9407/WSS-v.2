# Generated by Django 5.0.6 on 2024-07-31 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importwares', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rackplace',
            name='pallet_place',
        ),
        migrations.AddField(
            model_name='warehousepallet',
            name='is_assigned',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='PalletPlace',
        ),
        migrations.DeleteModel(
            name='RackPlace',
        ),
    ]
