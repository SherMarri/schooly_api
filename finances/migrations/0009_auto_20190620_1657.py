# Generated by Django 2.2.1 on 2019-06-20 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0008_auto_20190518_1927'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feechallan',
            name='structure',
        ),
        migrations.AddField(
            model_name='feechallan',
            name='break_down',
            field=models.TextField(default='{tuition: 0}', max_length=2048),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='feechallan',
            name='paid',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
