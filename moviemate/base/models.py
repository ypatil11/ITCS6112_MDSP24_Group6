from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MovieGoer(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    is_subscribed = models.BooleanField(null=False, default=False)

class MoviePreferences(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=255, null=False)
    cinema_name = models.CharField(max_length=255, null=False, default="xxxxxxxxxxxxxxxxxx")
    movie_name = models.CharField(max_length=255, null=False, default="xxxxxxxxxxxxxxxxxx")
    date =  models.DateField(blank=False, null=False)
    number_of_seats = models.IntegerField(null=False)
    time_from = models.IntegerField(null=False)
    time_to = models.IntegerField(null=False)
    is_processed = models.BooleanField(null=False, default=False)
    
class SeatPreferences(models.Model):
    preference = models.ForeignKey(MoviePreferences,  on_delete=models.CASCADE)
    number_of_rows_left = models.IntegerField(null=False, default=0)
    number_of_rows_top = models.IntegerField(null=False, default=0)
    is_included = models.BooleanField(null=False, default=False)