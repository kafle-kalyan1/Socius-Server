# Generated by Django 5.0.1 on 2024-03-09 13:09

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0008_reportpost'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ReportPost',
            new_name='Report',
        ),
    ]
