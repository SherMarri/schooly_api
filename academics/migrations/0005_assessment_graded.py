# Generated by Django 2.2.1 on 2019-10-22 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0004_merge_20191016_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='graded',
            field=models.BooleanField(default=True),
        ),
    ]
