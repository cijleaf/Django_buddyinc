import json
import requests

from django.conf import settings


LAMBDA_URL = "https://6igeev3nj9.execute-api.us-east-1.amazonaws.com/dev/load-zone"


def geocode(address):
    """ Get geo code of address.  Returns data of the form {"lat": 42.321654, "lng": -71.123456} """
    if settings.USE_FAKE:
        # lat/lng of 145 VT-100, West Dover, VT 05356, USA
        return {"lat": 42.940526, "lng": -72.856729}
    else:
        params = {
            'key': settings.GOOGLE_API_KEY,
            'address': address
        }
        r = requests.get(settings.GOOGLE_API_URL, params=params)
        data = r.json()
        if (r.status_code == 200 and 'results' in data and len(data['results']) > 0
            and 'geometry' in data['results'][0] and 'location' in data['results'][0]['geometry']):
            return data['results'][0]['geometry']['location']
        return None


def get_loadzone(latitude, longitude):
    """ Takes inputs of the form: 42.321654, -71.123456 """
    body = json.dumps({"latitude": latitude, "longitude": longitude})
    response = requests.post(LAMBDA_URL, body)
    response = response.json()

    if ("load_zone" not in response):
        if ("errorMessage" in response):
            raise Exception(response["errorMessage"])
        else:
            raise Exception("Error occured while looking up load zone")

    return response["load_zone"]
