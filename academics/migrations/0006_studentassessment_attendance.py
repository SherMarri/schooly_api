# Generated by Django 2.2.1 on 2019-10-23 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0005_assessment_graded'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentassessment',
            name='attendance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='academics.Assessment'),
        ),
    ]
