# Generated by Django 2.2.1 on 2019-11-04 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0004_auto_20190522_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='name',
            field=models.CharField(max_length=20),
        ),
    ]
