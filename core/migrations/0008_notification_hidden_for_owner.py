# Generated by Django 5.1.4 on 2025-07-11 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='hidden_for_owner',
            field=models.BooleanField(default=False),
        ),
    ]
