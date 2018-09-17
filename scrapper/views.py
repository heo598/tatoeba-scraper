import re
import requests
from bs4 import BeautifulSoup

from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST'])
def scrap(request):
    try:
        page = requests.get(request.data['url'])

        soup = BeautifulSoup(page.text, features="html.parser")
        
        results = re.findall('\d+', soup.find_all("h2")[1].text)
        
        if len(results) == 0:
            return Response({'data': [], 'numberOfResults': 0}, page.status_code)
        
        response = {
            'numberOfResults': results[0] if len(results) == 1 else results[1],
            'data': []
        }

        containers = soup.find_all("div", class_="sentence-and-translations")

        for container in containers:
            translations = []
            translationsContainers = container.findAll(class_="translation")

            for translation in translationsContainers:
                translations.append({
                    "text": translation.find(class_="text").text.strip(),
                    "language": translation.find(class_="lang").find("img").get('alt'),
                    "id": translation.find("md-button").get("href")[20::],
                    "direct": 'direct' in translation.find_parent("div").get("class")
                })
                
            response['data'].append({
                "text": container.find(class_="text").text.strip(),
                "language": container.find(class_="lang").find("img").get('alt'),
                "id": container.find("md-button").get("href")[20::],
                "translations": translations
            })
            
        return Response(response, page.status_code)
    except Exception as e:
        return Response(status=500)

