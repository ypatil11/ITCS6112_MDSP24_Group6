# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
import json
from .models import *
from django.utils.safestring import mark_safe
from django.utils.dateparse import parse_datetime

from django.shortcuts import render, redirect
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

import cachetools.func

def home(request):
    movie_preferences = []
    if request.user.is_authenticated:
        movie_preferences = MoviePreferences.objects.filter(user_id=request.user)
    
    else:
        return redirect('login')
    context = {'movie_preferences': movie_preferences}
    return render(request, 'home.html', context)




@login_required
def add_movie_preference(request):

    cities = get_cities()

    if request.method == 'POST':
        city = request.POST.get('city')
        cinema_name = request.POST.get('cinema_name')
        movie_name = request.POST.get('movie_name')
        date = parse_datetime(request.POST.get('date'))  # Ensuring proper datetime format
        number_of_seats = request.POST.get('number_of_seats')
        time_from = request.POST.get('time_from')
        time_to = request.POST.get('time_to')

        if city and movie_name and date and number_of_seats and time_from and time_to:
            number_of_seats = int(number_of_seats)
            time_from = int(time_from)
            time_to = int(time_to)

            new_pref = MoviePreferences(
                user=request.user,
                city=city,
                cinema_name=cinema_name,
                movie_name=movie_name,
                date=date,
                number_of_seats=number_of_seats,
                time_from=time_from,
                time_to=time_to,
                is_processed=False 
            )
            new_pref.save()

            new_seat_pref =  SeatPreferences(
                    preference = new_pref,
                    number_of_rows_left=0,
                    number_of_rows_top=0,
                    is_included=False,

            )
            new_seat_pref.save()
            return redirect('home')
        else:
            context = {
                'error': 'Missing information. Please fill out all fields.'
            }
            return render(request, 'preference_form.html', context)

    # GET request: just render the form
    context = { "cities": cities}
    return render(request, 'preference_form.html', context)


@login_required
def add_selecting(request, pk=None):
    if pk:
        movie_pref = get_object_or_404(MoviePreferences, pk=pk)
        try:
            seat_pref = SeatPreferences.objects.get(preference_id=movie_pref)
        except SeatPreferences.DoesNotExist:
            seat_pref = None
    else:
        movie_pref = None
        seat_pref = None

    if request.method == 'POST':
        number_of_rows_left = int(request.POST.get('number_of_rows_left'))
        number_of_rows_top = int(request.POST.get('number_of_rows_top'))
        is_included = request.POST.get('is_included') == 'on'

        if seat_pref:
            seat_pref.number_of_rows_left = number_of_rows_left
            seat_pref.number_of_rows_top = number_of_rows_top
            seat_pref.is_included = is_included
            seat_pref.save()
        else:
            seat_pref = SeatPreferences(
                preference_id=movie_pref,
                number_of_rows_left=number_of_rows_left,
                number_of_rows_top=number_of_rows_top,
                is_included=is_included
            )
            seat_pref.save()

        return redirect('home')  # Redirect to home or another appropriate page

    context = {
        'seat_pref': seat_pref,
        'movie_pref': movie_pref,
        'pk': pk
    }
    return render(request, 'seat_pref.html', context)

@login_required
def delete_movie_pref(request, pk=None):
    movie_pref = get_object_or_404(MoviePreferences, pk=pk, user_id=request.user)
    movie_pref.delete()

    return redirect('home')

@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_cities():
    driver = uc.Chrome()
    cinemalist_url = "https://in.bookmyshow.com/explore/cinemas"
    driver.get(cinemalist_url)
    driver.find_element(By.XPATH, "//span[contains(@cursor,'pointer')]").click()
    
    # Major Cities
    city_list_elements_major = driver.find_elements(By.XPATH, "//li//child::div//child::span")
    city_list = [city.get_attribute("innerHTML") for city in city_list_elements_major]
        
    driver.close()
    
    return city_list

@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_movie_from_city(request, city=None):
    driver = uc.Chrome()
    
    movieslist_url = f"https://in.bookmyshow.com/explore/movies-{city}"
    driver.get(movieslist_url)
    driver.execute_script("window.scrollTo(0, 2000);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 3000);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 4000);")
    time.sleep(1)
    movie_list_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-7o7nez-0')]//ancestor::a//descendant::h3")
    movie_list = [movie.get_attribute("innerHTML") for movie in movie_list_elements]
    
    driver.close()
    
    return JsonResponse({"movies" : movie_list})


@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_cinema_from_city(request, city=None):
    driver = uc.Chrome()
    
    cinemalist_url = f"https://in.bookmyshow.com/{city}/cinemas"
    driver.get(cinemalist_url)
    driver.find_element(By.XPATH, f"//li//child::div//child::span[contains(text(), '{city}')]").click()
    time.sleep(2)
    cinema_list_elements = driver.find_elements(By.XPATH, "//div//div//div//div//div//div//div//div//div//div")
    cinema_list = [city.get_attribute("innerHTML") for city in cinema_list_elements[::2]]
    
    driver.close()

    return JsonResponse({"cinemas" : cinema_list})


def signup_user(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        try:
            User.objects.create_user(username=username, password=password, email=email)
        except Exception as e:
            context={'errormsg': "1"}
            render(request, 'signup.html', context)
        else:
            # Redirect to the desired page after successful signup
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to the desired page after login
                return redirect('home')


    return render(request, 'signup.html', context)


def login_user(request):
     
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the distributor's dashboard or desired page after login
            return redirect('home')

    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('home')