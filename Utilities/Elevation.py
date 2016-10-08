import requests

api_key = 'AIzaSyBeGPwcHurxHOASNSG4m4G6UdY2ADEdoN0'

def getElevation(lat,lon):
	elevation_response = requests.post("https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(lat) + ',' + str(lon) + "&key=" + api_key)
	elevation_response_dict = elevation_response.json()
	return elevation_response_dict['results'][0]['elevation']