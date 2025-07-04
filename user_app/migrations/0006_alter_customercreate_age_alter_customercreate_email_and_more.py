# Generated by Django 5.2.1 on 2025-05-30 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0005_customercreate_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customercreate',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customercreate',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='customercreate',
            name='phone',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
