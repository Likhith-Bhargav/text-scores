# Generated by Django 4.2.2 on 2025-01-21 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextCount',
            fields=[
                ('serial_number', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.TextField(unique=True)),
                ('count', models.IntegerField(default=2)),
            ],
        ),
    ]
