# Generated by Django 4.0 on 2022-01-29 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_phonenumberotp_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumberotp',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='phonenumberotp',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
