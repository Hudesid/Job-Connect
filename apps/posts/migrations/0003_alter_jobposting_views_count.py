# Generated by Django 5.1.6 on 2025-03-21 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobposting',
            name='views_count',
            field=models.IntegerField(default=0),
        ),
    ]
