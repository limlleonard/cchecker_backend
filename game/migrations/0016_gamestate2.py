# Generated by Django 5.1.7 on 2025-03-28 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0015_rename_nrmove_gamestate1_movenr_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameState2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roomnr', models.IntegerField(unique=True)),
                ('playernr', models.IntegerField(default=1)),
                ('turnwise', models.IntegerField(default=0)),
                ('movenr', models.IntegerField(default=0)),
            ],
        ),
    ]
