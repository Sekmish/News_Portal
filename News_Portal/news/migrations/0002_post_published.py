# Generated by Django 5.0.3 on 2024-03-20 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='published',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
