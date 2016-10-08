import json

import credential_file
import requests


def google_location(mob_country, mob_network, radio_type, carrier, cell_towers, wifi_points):
    for i, tower in enumerate(cell_towers):
        del tower["timestamp"]
        cell_towers[i] = tower
    for i, wifi in enumerate(wifi_points):
        #del wifi["timestamp"]
        wifi_points[i] = wifi

    google_req = requests.post(
        "https://www.googleapis.com/geolocation/v1/geolocate?key=" + credential_file.google_api_key,
        data=json.dumps({
            "homeMobileCountryCode": mob_country,
            "homeMobileNetworkCode": mob_network,
            "radioType": radio_type,
            "carrier": carrier,
            "considerIp": "false",
            "cellTowers": json.dumps(cell_towers),
            "wifiAccessPoints": json.dumps(wifi_points)
        }),
        headers={'Content-Type': 'application/json'})

    google_return = json.loads(google_req.text)

    try:
        lat = float(google_return["location"]["lat"])
        lng = float(google_return["location"]["lng"])
        accuracy = float(google_return["accuracy"])
    except:
        return None

    return [lat, lng, accuracy]
