from django.urls import path
from .views import popularity, restaurant_detail, search_restaurants

urlpatterns = [
    path('popularity/', popularity, name = 'home'),
    path('search/', search_restaurants, name='search_restaurants'),
    path('restaurant/<int:restaurant_id>/', restaurant_detail, name='restaurant_detail'),
]

