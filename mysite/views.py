from django.shortcuts import render,redirect
import requests

def index(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=67fa12d425425aea723017c56ce020e7'
    city='Ajdovščina'
    requestWeather=requests.get(url.format(city)).json()

    city_weather = {
        'city': city,
        'state': requestWeather['sys']['country'],
        'temperature': requestWeather['main']['temp'],
        'description': requestWeather['weather'][0]['description'],
        'icon': requestWeather['weather'][0]['icon'],
        'wind': requestWeather['wind']['speed'],
    }

    url_randomJoke = 'http://api.icndb.com/jokes/random/'
    whole_joke = requests.get(url_randomJoke).json()
    random_joke = {
        'id': whole_joke['value']['id'],
        'joke': whole_joke['value']['joke'],
    }

    context = {'city_weather': city_weather,
               'random_joke':random_joke}

    return render(request,'mysite.html', context)