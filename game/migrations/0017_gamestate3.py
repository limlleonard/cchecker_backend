# Generated by Django 5.1.7 on 2025-03-28 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0016_gamestate2'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameState3',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roomnr', models.IntegerField(unique=True)),
                ('playernr', models.IntegerField(default=1)),
                ('turnwise', models.IntegerField(default=0)),
                ('movenr', models.IntegerField(default=0)),
                ('selected', models.JSONField(blank=True, default=None, null=True)),
                ('valid_pos', models.JSONField(blank=True, default=None, null=True)),
            ],
        ),
    ]
