# Generated by Django 4.2.3 on 2023-07-23 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welearn', '0019_alter_category_options_alter_content_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
