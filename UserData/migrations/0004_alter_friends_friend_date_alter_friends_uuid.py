# Generated by Django 4.2.7 on 2023-12-26 01:46

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('UserData', '0003_remove_friends_friend_remove_friends_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friends',
            name='friend_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='friends',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('7c60cf53-9368-4980-b406-01c52cb001b8'), editable=False, primary_key=True, serialize=False),
        ),
    ]
