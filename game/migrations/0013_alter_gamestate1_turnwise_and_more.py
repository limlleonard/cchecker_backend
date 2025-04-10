# Generated by Django 5.1.7 on 2025-03-28 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0012_gamestate1_nrmove'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamestate1',
            name='turnwise',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='gamestatebetween1',
            name='selected',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='gamestatebetween1',
            name='valid_pos',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
