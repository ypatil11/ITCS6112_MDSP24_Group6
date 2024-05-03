# Generated by Django 4.2.11 on 2024-04-30 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_moviepreferences_user_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seatpreferences',
            name='movie_name',
        ),
        migrations.RemoveField(
            model_name='seatpreferences',
            name='number_of_rows',
        ),
        migrations.RemoveField(
            model_name='seatpreferences',
            name='side',
        ),
        migrations.AddField(
            model_name='seatpreferences',
            name='number_of_rows_bottom',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='seatpreferences',
            name='number_of_rows_left',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='seatpreferences',
            name='number_of_rows_right',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='seatpreferences',
            name='number_of_rows_top',
            field=models.IntegerField(default=0),
        ),
    ]
