# Generated by Django 2.2.1 on 2019-12-05 07:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0008_auto_20191009_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffattendanceitem',
            name='submitted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submitted_staff_attendances', to=settings.AUTH_USER_MODEL),
        ),
    ]