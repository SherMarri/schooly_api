# Generated by Django 2.2.1 on 2019-07-29 20:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_auto_20190729_2042'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staffattendance',
            old_name='user',
            new_name='employee',
        ),
        migrations.RenameField(
            model_name='studentattendance',
            old_name='user',
            new_name='student',
        ),
    ]
