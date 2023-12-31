# Generated by Django 4.2.3 on 2023-07-22 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welearn', '0011_content_youtube_video_alter_content_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizattempt',
            name='is_passed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='course',
            name='registered_users',
            field=models.ManyToManyField(blank=True, null=True, related_name='registered_courses', to='welearn.weuser'),
        ),
    ]
