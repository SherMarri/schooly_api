# Generated by Django 2.2.1 on 2019-10-09 18:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('structure', '0004_auto_20190522_2256'),
        ('attendance', '0004_auto_20190729_2046'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyStaffAttendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('date', models.DateField()),
                ('average_attendance', models.FloatField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_staff_attendances', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DailyStudentAttendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('date', models.DateField()),
                ('average_attendance', models.FloatField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_student_attendances', to=settings.AUTH_USER_MODEL)),
                ('section', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_attendances', to='structure.Section')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StaffAttendanceItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('status', models.IntegerField(blank=True, choices=[(1, 'Present'), (2, 'Absent'), (3, 'Leave')], null=True)),
                ('comments', models.TextField(max_length=128)),
                ('date', models.DateField()),
                ('attendance', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='attendance.DailyStaffAttendance')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_attendances', to=settings.AUTH_USER_MODEL)),
                ('submitted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_staff_attendances', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StudentAttendanceItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('status', models.IntegerField(blank=True, choices=[(1, 'Present'), (2, 'Absent'), (3, 'Leave')], null=True)),
                ('comments', models.TextField(max_length=128)),
                ('date', models.DateField()),
                ('attendance', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='attendance.DailyStudentAttendance')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_attendances', to=settings.AUTH_USER_MODEL)),
                ('submitted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_student_attendances', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='studentattendance',
            name='student',
        ),
        migrations.RemoveField(
            model_name='studentattendance',
            name='submitted_by',
        ),
        migrations.DeleteModel(
            name='StaffAttendance',
        ),
        migrations.DeleteModel(
            name='StudentAttendance',
        ),
    ]
