# Generated by Django 4.2.3 on 2023-07-23 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welearn', '0014_mail'),
    ]

    operations = [
        migrations.AddField(
            model_name='tier',
            name='price',
            field=models.IntegerField(default=50),
        ),
    ]