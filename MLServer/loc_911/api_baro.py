import requests
import credential_file

LEVEL_HEIGHT = 3.0
PRESSURE_API_CALI = -3


def get_floor(lat, lon, baro):
    height = get_temperature(lat, lon) / (-0.0065) * (
        (baro / (get_sealevel_pressure(lat, lon) + PRESSURE_API_CALI)) ** (8.31432 * 0.0065 / 9.80665 / 0.0289644) - 1)
    level = (height - get_elevation(lat, lon)) / float(LEVEL_HEIGHT)
    return int(level)


def get_sealevel_pressure(lat, lon):
    weather_response = requests.post(
        "http://api.openweathermap.org/data/2.5/weather?APPID=" + credential_file.weather_key + "&lat=" + str(
            lat) + "&lon=" + str(lon))
    weather_response_dict = weather_response.json()
    return weather_response_dict['main']['pressure']


def get_temperature(lat, lon):
    weather_response = requests.post(
        "http://api.openweathermap.org/data/2.5/weather?APPID=" + credential_file.weather_key + "&lat=" + str(
            lat) + "&lon=" + str(lon))
    weather_response_dict = weather_response.json()
    return weather_response_dict['main']['temp']


def get_elevation(lat, lon):
    elevation_response = requests.post(
        "https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(lat) + ',' + str(
            lon) + "&key=" + credential_file.google_api_key)
    elevation_response_dict = elevation_response.json()
    return elevation_response_dict['results'][0]['elevation']


# for testing only
if __name__ == "__main__":
    print get_floor(40.8094, -73.9609, 1010.0)
