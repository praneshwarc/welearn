# Generated by Django 4.2.3 on 2023-07-22 01:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('welearn', '0009_alter_content_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='weuser',
            name='tier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='welearn.tier'),
        ),
        migrations.AlterField(
            model_name='module',
            name='description',
            field=models.TextField(max_length=500),
        ),
    ]