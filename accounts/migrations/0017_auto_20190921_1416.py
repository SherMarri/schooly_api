# Generated by Django 2.2.1 on 2019-09-21 14:16

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auto_20190919_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffinfo',
            name='date_hired',
            field=models.DateField(default=datetime.datetime(2019, 9, 21, 14, 16, 56, 241605, tzinfo=utc)),
        ),
    ]
