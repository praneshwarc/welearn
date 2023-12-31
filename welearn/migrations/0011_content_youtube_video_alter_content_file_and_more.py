# Generated by Django 4.2.3 on 2023-07-22 03:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('welearn', '0010_weuser_tier_alter_module_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='youtube_video',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='content',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='course',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='welearn.weuser'),
        ),
        migrations.AlterField(
            model_name='option',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='welearn.question'),
        ),
        migrations.AlterField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='welearn.quiz'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='module',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='quiz', to='welearn.module'),
        ),
    ]
