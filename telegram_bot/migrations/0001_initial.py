# Generated by Django 3.0.4 on 2020-03-14 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.IntegerField()),
                ('tuewarning', models.BooleanField(default=False)),
                ('citieswarning', models.TextField()),
            ],
        ),
    ]
