# Generated by Django 4.2.11 on 2024-04-30 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_rename_preference_id_seatpreferences_preference_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seatpreferences',
            name='number_of_rows_bottom',
        ),
        migrations.RemoveField(
            model_name='seatpreferences',
            name='number_of_rows_right',
        ),
        migrations.AddField(
            model_name='moviepreferences',
            name='cinema_name',
            field=models.CharField(default='xxxxxxxxxxxxxxxxxx', max_length=255),
        ),
        migrations.AlterField(
            model_name='moviepreferences',
            name='movie_name',
            field=models.CharField(default='xxxxxxxxxxxxxxxxxx', max_length=255),
        ),
    ]