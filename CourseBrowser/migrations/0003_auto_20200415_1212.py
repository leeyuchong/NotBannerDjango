# Generated by Django 3.0.5 on 2020-04-15 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CourseBrowser', '0002_remove_courses_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='courses',
            name='limits',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='courses',
            name='requests',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
