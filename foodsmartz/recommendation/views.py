from django.shortcuts import render
from .model import popularity_based, restaurant_recommendations, find_restaurant_by_id
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
import pandas as pd
from fuzzywuzzy import process

df = pd.read_csv('C:\\Users\\harshit.vashistha\\Desktop\\Recommendation project\\foodsmartz\\recommendation\\dataset\\recommendation_data.csv')

df.reset_index(inplace=True) 

class SmallPageNumberPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 10

def popularity(request):
    global df
    popular = popularity_based(df).sort_values('rate', ascending=False)
    restaurants = popular.to_dict(orient='records')

    page_number = request.GET.get('page', 1)
    paginator = Paginator(restaurants, 10) 

    try:
        paginated_restaurants = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_restaurants = paginator.page(1) 
    except EmptyPage:
        paginated_restaurants = paginator.page(paginator.num_pages)  

    return render(request, 'home.html', {
        'restaurants': paginated_restaurants,
        'page': paginated_restaurants,
        'page_count': paginator.num_pages,
    })


def restaurant_detail(request, restaurant_id):
    global df
    restaurant = find_restaurant_by_id(df, restaurant_id)

    if restaurant is not None and not restaurant.empty:
        res_name = restaurant['name'] 
        recommendations = restaurant_recommendations(df, res_name)
    else:
        restaurant = None
        recommendations = {'restaurants': []}  

    return render(request, 'detail.html', {
        'restaurant': restaurant,
        'recommendations': recommendations['restaurants'],
    })



def search_restaurants(request):
    query = request.GET.get('restaurant', '').strip()
    restaurants = []

    if query:
        global df
        df = df.drop_duplicates(subset=['name', 'location'])
        restaurant_names = df['name'].tolist()
        matched_names = process.extract(query, restaurant_names, limit=None)

        threshold = 80  
        similar_names = [name for name, score in matched_names if score >= threshold]
        
        filtered_df = df[df['name'].isin(similar_names) | 
                          df['location'].str.contains(query, case=False) | 
                          df['address'].str.contains(query, case=False)]

        restaurants = filtered_df.to_dict(orient='records')

    page_number = request.GET.get('page', 1)
    paginator = Paginator(restaurants, 10)

    try:
        paginated_restaurants = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_restaurants = paginator.page(1)
    except EmptyPage:
        paginated_restaurants = paginator.page(paginator.num_pages)

    return render(request, 'home.html', {
        'restaurants': paginated_restaurants,
        'page': paginated_restaurants,
        'page_count': paginator.num_pages,
        'request': request
    })



