# Generated by Django 2.2.1 on 2019-05-17 19:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('accounts', '0002_studentinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='profile',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
