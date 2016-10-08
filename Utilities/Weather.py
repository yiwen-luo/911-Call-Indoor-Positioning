import requests

api_key = '91d836f79b703c49bb6c0bd32724351a'

def getCurrentSeaLevelPressure(lat, lon):
	weather_response = requests.post("http://api.openweathermap.org/data/2.5/weather?APPID=" + api_key + "&lat=" + str(lat) + "&lon=" + str(lon))
	weather_response_dict = weather_response.json()
	return weather_response_dict['main']['pressure']

def getCurrentTemperature(lat, lon):
	weather_response = requests.post("http://api.openweathermap.org/data/2.5/weather?APPID=" + api_key + "&lat=" + str(lat) + "&lon=" + str(lon))
	weather_response_dict = weather_response.json()
	return weather_response_dict['main']['temp']