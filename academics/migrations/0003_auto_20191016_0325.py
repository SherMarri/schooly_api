# Generated by Django 2.2.1 on 2019-10-16 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0002_assessment_studentassessment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentassessment',
            name='comments',
            field=models.TextField(blank=True, max_length=128, null=True),
        ),
    ]
