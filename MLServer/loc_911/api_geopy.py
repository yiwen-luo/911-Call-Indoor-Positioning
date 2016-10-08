from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def get_address(lat, lng):
    try:
        geolocator = Nominatim()
        location = geolocator.reverse(str(lat) + "," + str(lng))
        return location.address
    except GeocoderTimedOut:
        print "Geopy timed out."
        return get_address(lat, lng)
    except:
        return None

