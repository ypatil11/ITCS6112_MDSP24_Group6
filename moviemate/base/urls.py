from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('signup/', views.signup_user, name="signup"),
    # path('home/', views.home, name="home"),
    path('get-movies/<str:city>', views.get_movie_from_city, name="get_movie_from_city"),
    path('get-cinemas/<str:city>', views.get_cinema_from_city, name="get_cinema_from_city"),

    path('add_movie_preference/', views.add_movie_preference, name="add_movie_preference"),
    path('add_selecting/<str:pk>', views.add_selecting, name="add_selecting"),
    path('delete_movie_pref/<str:pk>', views.delete_movie_pref, name="delete_movie_pref"),
]