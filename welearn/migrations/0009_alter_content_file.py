# Generated by Django 4.2.3 on 2023-07-21 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welearn', '0008_alter_content_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='file',
            field=models.FileField(upload_to=''),
        ),
    ]