# Generated by Django 5.1.6 on 2025-03-22 01:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_alter_jobseeker_phone_number_alter_token_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 22, 1, 44, 47, 13923, tzinfo=datetime.timezone.utc)),
        ),
    ]
