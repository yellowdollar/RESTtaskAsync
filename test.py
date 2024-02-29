import httpx
import json
from pprint import pprint

import asyncio

async def request_to_service():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 38.5358,
        "longitude": 68.779,
        "current": "temperature_2m",
        "hourly": ["temperature_2m", "rain", "snowfall"]
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response_json = response.json()

    weather_dushanbe = {
        'temperature': response_json['hourly']['temperature_2m'][0:10],
        'time': response_json['hourly']['time'][0:10],
        'snowfall': response_json['hourly']['snowfall'][0:10],
        'rain': response_json['hourly']['rain'][0:10]
    }

    return json.loads(json.dumps(weather_dushanbe))

async def second_request(id):
    url = f'https://jsonplaceholder.org/posts?id={id}'

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response_json = response.json()


    return response_json