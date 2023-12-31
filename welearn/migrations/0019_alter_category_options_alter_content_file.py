# Generated by Django 4.2.3 on 2023-07-23 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welearn', '0018_userbillinginfo_paypal_pid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['label'], 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterField(
            model_name='content',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='static/uploads/'),
        ),
    ]
