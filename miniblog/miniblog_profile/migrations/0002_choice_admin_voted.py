# Generated by Django 4.2.8 on 2023-12-18 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miniblog_profile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='admin_voted',
            field=models.BooleanField(default=False),
        ),
    ]
