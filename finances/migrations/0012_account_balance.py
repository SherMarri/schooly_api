# Generated by Django 2.2.1 on 2019-07-10 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0011_account_transaction_transactioncategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='balance',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
