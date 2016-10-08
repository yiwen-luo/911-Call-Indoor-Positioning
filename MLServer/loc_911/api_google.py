import json
from collections import OrderedDict
import credential_file
import requests


def google_location(mob_country, mob_network, radio_type, carrier, cell_towers, wifi_points):
    cell_towers_send = []
    for i, tower in enumerate(cell_towers):
        cell_towers_send_temp = OrderedDict()
        cell_towers_send_temp["cellId"] = tower["cellId"]
        cell_towers_send_temp["locationAreaCode"] = tower["locationAreaCode"]
        cell_towers_send_temp["mobileCountryCode"] = tower["mobileCountryCode"]
        cell_towers_send_temp["mobileNetworkCode"] = tower["mobileNetworkCode"]
        cell_towers_send.append(cell_towers_send_temp)

    wifi_points_send = []
    for i, wifi in enumerate(wifi_points):
        wifi_points_send_temp = OrderedDict()
        wifi_points_send_temp["macAddress"] = wifi["BSSID"]
        wifi_points_send_temp["signalStrength"] = wifi["RSSI"]
        wifi_points_send_temp["age"] = 0
        channel = frequency_channel(wifi["frequency"])
        if channel > 0:
            wifi_points_send_temp["channel"] = channel
        wifi_points_send.append(wifi_points_send_temp)

    google_req = requests.post(
        "https://www.googleapis.com/geolocation/v1/geolocate?key=" + credential_file.google_api_key,
        data=json.dumps({
            "homeMobileCountryCode": mob_country,
            "homeMobileNetworkCode": mob_network,
            "radioType": radio_type,
            "carrier": carrier,
            "considerIp": "false",
            "cellTowers": cell_towers_send,
            "wifiAccessPoints": wifi_points_send
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


def frequency_channel(freq):
    if 2142 <= freq < 2484:
        return (freq - 2142) / 5 + 1
    elif 5170 <= freq < 5330:
        return (freq - 5170) / 20 * 4 + 36
    elif 5490 <= freq < 5730:
        return (freq - 5490) / 20 * 4 + 100
    elif 5735 <= freq < 5835:
        return (freq - 5735) / 20 * 4 + 149
    else:
        return 0
