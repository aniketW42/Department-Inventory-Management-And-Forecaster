# Generated by Django 4.2.7 on 2025-07-03 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_remove_inventoryitem_last_maintenance_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventoryitem',
            name='date_added',
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='last_maintenance_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
