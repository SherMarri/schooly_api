# Generated by Django 2.2.1 on 2019-05-17 23:29

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0006_auto_20190518_0308'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenseitem',
            name='date',
            field=models.DateField(default=datetime.datetime(2019, 5, 17, 23, 28, 58, 137105, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='incomeitem',
            name='date',
            field=models.DateField(default=datetime.datetime(2019, 5, 17, 23, 29, 3, 257422, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
