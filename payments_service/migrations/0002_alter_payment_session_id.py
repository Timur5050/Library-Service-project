# Generated by Django 5.0.8 on 2024-08-27 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments_service', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='session_id',
            field=models.CharField(max_length=500),
        ),
    ]
