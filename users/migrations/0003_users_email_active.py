# Generated by Django 3.2.18 on 2023-10-11 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_users_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='email_active',
            field=models.BooleanField(default=False, verbose_name='邮箱验证状态'),
        ),
    ]