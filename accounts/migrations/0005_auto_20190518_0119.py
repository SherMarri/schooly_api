# Generated by Django 2.2.1 on 2019-05-17 20:19

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20190518_0056'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('date_hired', models.DateField(auto_now_add=True)),
                ('salary', models.FloatField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StaffInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('fullname', models.CharField(max_length=128)),
                ('contact', models.CharField(blank=True, max_length=20, null=True)),
                ('date_hired', models.DateField(auto_now_add=True)),
                ('salary', models.FloatField(default=0)),
                ('designation', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TeacherInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('fullname', models.CharField(max_length=128)),
                ('contact', models.CharField(blank=True, max_length=20, null=True)),
                ('date_hired', models.DateField(auto_now_add=True)),
                ('salary', models.FloatField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='profile',
            name='contact',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='studentinfo',
            name='user',
        ),
        migrations.AddField(
            model_name='studentinfo',
            name='contact',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='studentinfo',
            name='date_enrolled',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentinfo',
            name='fullname',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_type',
            field=models.IntegerField(choices=[(1, 'Admin'), (2, 'Staff'), (3, 'Teacher'), (4, 'Student'), (5, 'Parent')]),
        ),
        migrations.AlterField(
            model_name='studentinfo',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='structure.Section'),
        ),
    ]
