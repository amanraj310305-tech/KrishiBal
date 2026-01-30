
import os
import requests
from datetime import datetime


def get_farming_news():
    """
    Fetch farming-related news and government schemes
    """
    try:
        # Using NewsAPI (you'll need to get a free API key from https://newsapi.org/)
        api_key = os.getenv("NEWS_API_KEY")

        # Search for agriculture-related news
        url = f"https://newsapi.org/v2/everything?q=agriculture OR farming OR crops OR government schemes farmers&language=en&sortBy=publishedAt&apiKey={api_key}"

        response = requests.get(url)
        data = response.json()

        if data['status'] == 'ok':
            articles = data['articles'][:10]  # Get top 10 articles

            news_list = []
            for article in articles:
                news_item = {
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'source': article['source']['name'],
                    'published_at': article['publishedAt'],
                    'image': article['urlToImage']
                }
                news_list.append(news_item)

            return {'success': True, 'news': news_list}
        else:
            return {'success': False, 'error': 'Failed to fetch news'}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_government_schemes():
    """
    Fetch government schemes for farmers (you can customize this)
    """
    # This is a static list - you can integrate with government APIs if available
    schemes = [
        {
            'title': 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
            'description': '₹6000 per year in three equal installments to all landholding farmers',
            'link': 'https://pmkisan.gov.in/',
            'category': 'Financial Support'
        },
        {
            'title': 'Kisan Credit Card (KCC)',
            'description': 'Credit facility for farmers to purchase agriculture inputs and meet crop production expenses',
            'link': 'https://www.india.gov.in/spotlight/kisan-credit-card-kcc',
            'category': 'Credit Facility'
        },
        {
            'title': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
            'description': 'Crop insurance scheme providing financial support in case of crop failure',
            'link': 'https://pmfby.gov.in/',
            'category': 'Insurance'
        },
        {
            'title': 'Soil Health Card Scheme',
            'description': 'Provides soil health cards to farmers with crop-wise recommendations',
            'link': 'https://soilhealth.dac.gov.in/',
            'category': 'Soil Management'
        },
        {
            'title': 'Paramparagat Krishi Vikas Yojana (PKVY)',
            'description': 'Promotes organic farming and organic value chain development',
            'link': 'https://pgsindia-ncof.gov.in/',
            'category': 'Organic Farming'
        }
    ]

    return {'success': True, 'schemes': schemes}


def search_news(query):
    """
    Search for specific farming news based on query
    """
    try:
        api_key = os.getenv("NEWS_API_KEY")

        url = f"https://newsapi.org/v2/everything?q={query} farming agriculture&language=en&sortBy=relevancy&apiKey={api_key}"

        response = requests.get(url)
        data = response.json()

        if data['status'] == 'ok':
            articles = data['articles'][:5]

            news_list = []
            for article in articles:
                news_item = {
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'source': article['source']['name']
                }
                news_list.append(news_item)

            return {'success': True, 'news': news_list}
        else:
            return {'success': False, 'error': 'No news found'}

    except Exception as e:

        return {'success': False, 'error': str(e)}
