# Generated by Django 4.1 on 2024-03-21 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('due', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='due',
            name='payment_url',
            field=models.URLField(default=None, null=True),
        ),
    ]
