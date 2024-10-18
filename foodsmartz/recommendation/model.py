import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def popularity_based(df):    

    new_df = df.drop_duplicates(subset=['name', 'location'])
    popular_rest = new_df.sort_values('rate', ascending=False)
    return popular_rest


def restaurant_based(df, restaurant_name, num_recommendations=5, chunk_size=1000):
    df['combined'] = df['cuisines'] + " " + df['dish_liked']
    
    chunks = [df[i:i + chunk_size] for i in range(0, df.shape[0], chunk_size)]
    tfidf_vectorizer = TfidfVectorizer()
     
    similarity_scores_name = {}
    similarity_scores_dish = {}
    restaurant_details = None

    for chunk in chunks:
        tfidf_matrix_name = tfidf_vectorizer.fit_transform(chunk['name']) 
        cosine_sim_name = cosine_similarity(tfidf_matrix_name)

        tfidf_matrix_dish = tfidf_vectorizer.fit_transform(chunk['combined']) 
        cosine_sim_dish = cosine_similarity(tfidf_matrix_dish)

        if restaurant_name in chunk['name'].values: 
            restaurant_index = chunk.index.get_loc(chunk[chunk['name'] == restaurant_name].index[0])
            restaurant_details = chunk.iloc[restaurant_index]  
        else:
            continue

        for idx, score in enumerate(cosine_sim_name[restaurant_index]):
            if chunk.iloc[idx]['name'] != restaurant_name:  
                if chunk.iloc[idx]['name'] not in similarity_scores_name:
                    similarity_scores_name[chunk.iloc[idx]['name']] = {
                        'score': score,
                        'votes': chunk.iloc[idx]['votes'],
                        'rate': chunk.iloc[idx]['rate'],
                        'address': chunk.iloc[idx]['address'],
                        'location': chunk.iloc[idx]['location'],
                        'combined': chunk.iloc[idx]['combined']
                    }

        for idx, score in enumerate(cosine_sim_dish[restaurant_index]):
            if chunk.iloc[idx]['name'] != restaurant_name:  
                if chunk.iloc[idx]['name'] not in similarity_scores_dish:
                    similarity_scores_dish[chunk.iloc[idx]['name']] = {
                        'score': score,
                        'votes': chunk.iloc[idx]['votes'],
                        'rate': chunk.iloc[idx]['rate'],
                        'address': chunk.iloc[idx]['address'],
                        'location': chunk.iloc[idx]['location'],
                        'combined': chunk.iloc[idx]['combined']
                    }

    name_recommendations = sorted(similarity_scores_name.items(), key=lambda x: x[1]['score'], reverse=True)[:num_recommendations]
    dish_recommendations = sorted(similarity_scores_dish.items(), key=lambda x: x[1]['score'], reverse=True)[:num_recommendations]

    combined_recommendations = {name: details for name, details in name_recommendations}
    for name, details in dish_recommendations:
        if name not in combined_recommendations:
            combined_recommendations[name] = details

    combined_recommendations = list(combined_recommendations.items())[:num_recommendations * 2]

    formatted_recommendations = [
        {
            'name': name,
            'score': details['score'],
            'votes': details['votes'],
            'rate': details['rate'],
            'address': details['address'],
            'location': details['location'],
            'combined': details['combined'] 
        }
        for name, details in combined_recommendations
    ]


    if restaurant_details is not None:
        restaurant_info = {
            'name': restaurant_details['name'],
            'votes': restaurant_details['votes'],
            'rate': restaurant_details['rate'],
            'address': restaurant_details['address'],
            'location': restaurant_details['location'],
            'combined': restaurant_details['combined']
        }
    else:
        restaurant_info = None

    return {
        'restaurant_info': restaurant_info,
        'recommendations': formatted_recommendations
    }


def find_restaurant_by_id(df, index):
    if index in df['Unnamed: 0']:
        restaurant = df.loc[index] 
        return restaurant
    else:
        return None


def restaurant_recommendations(df, restaurant_name):
    restaurants = []
    restaurant_info = None  

    result = restaurant_based(df, restaurant_name)

    restaurant_info = result.get('restaurant_info')
    recommendations = result.get('recommendations', [])

    if recommendations:
        restaurants = [
            {
                'name': details['name'],
                'score': details['score'],
                'votes': details['votes'],
                'rate': details['rate'],
                'address': details['address'],
                'location': details['location'],
                'combined': details['combined']
            }
            for details in recommendations
        ]

    return {
        'restaurants': restaurants, 
        'restaurant_info': restaurant_info, 
    }

