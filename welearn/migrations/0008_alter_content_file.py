# Generated by Django 4.2.3 on 2023-07-21 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welearn', '0007_alter_module_unique_together_remove_module_ordering'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='file',
            field=models.FileField(upload_to='media/'),
        ),
    ]
