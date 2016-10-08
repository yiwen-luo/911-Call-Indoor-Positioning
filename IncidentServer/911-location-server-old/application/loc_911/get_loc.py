# This package is developed by Yiwen Luo (yiwen.luo@columbia.edu)

import json
import credential_file
import get_google
import get_tagged
import knn


def get_now(raw_data):
    """
    sample input:
    {u'addrJSON': '{"street": "3301 Broadway"}',
     u'GPSLat': 0,
     'timestamp': 1462659350.013805,
     u'pressure': 0,
     u'cellTowerJSON': '{"cellTowers": [{"signalStrength": -79,
                                        "timestamp": 54823832,
                                        "locationAreaCode": 52178,
                                        "mobileCountryCode": 310,
                                        "cellId": 183577101,
                                        "mobileNetworkCode": 260}],
                        "homeMobileCountryCode": 310,
                        "carrier": "T-Mobile",
                        "homeMobileNetworkCode": 260,
                        "radioType": "WCDMA"}',
     u'indoorFlag': True,
     u'wifiJSON': '[{"RSSI": -56, "frequency": 5200, "SSID": "Columbia University", "BSSID": "d8:c7:c8:2d:31", "timestamp": 54823832}, '
                  '{"RSSI": -56, "frequency": 5200, "SSID": "eduroam", "BSSID": "d8:c7:c8:2d:31", "timestamp": 54823832}]',
     u'GPSAlt': 0,
     u'GPSLong': 0,
     'addr_id': 132,
     u'GPSAccu': 0}

    output: [lat, lng, acc]

    """

    result = ""

    #raw_data = json.loads(raw_data)
    cell_data = json.loads(raw_data["cellTowerJSON"])
    wifi_data = json.loads(raw_data["wifiJSON"])

    # Get data from GPS
    gps_lat = float(raw_data["GPSLat"])
    gps_lng = float(raw_data["GPSLong"])

    # Get data from tagged database
    tagged_addrs = get_tagged.from_db(gps_lat, gps_lng, 0.01)

    # Get data from Google API
    google_result = get_google.google_location(
    cell_data["homeMobileCountryCode"],
    cell_data["homeMobileNetworkCode"],
    cell_data["radioType"].lower(),
    cell_data["carrier"],
    cell_data["cellTowers"],
    wifi_data)
    try:
        google_result = get_google.google_location(
            cell_data["homeMobileCountryCode"],
            cell_data["homeMobileNetworkCode"],
            cell_data["radioType"].lower(),
            cell_data["carrier"],
            cell_data["cellTowers"],
            raw_data["wifiJSON"])

    except:
        print "Google API error!"

    print google_result

    if google_result:
        return str(google_result)
    else:
        return "Temporarily no data available"


if __name__ == "__main__":
    raw_data = json.dumps({'addrJSON': {"street": "3301 Broadway"},
                           'GPSLat': 0,
                           'timestamp': 1462659350.013805,
                           'pressure': 0,
                           'cellTowerJSON': {"cellTowers": [{"signalStrength": -79,
                                                             "timestamp": 54823832,
                                                             "locationAreaCode": 52178,
                                                             "mobileCountryCode": 310,
                                                             "cellId": 183577101,
                                                             "mobileNetworkCode": 260}],
                                             "homeMobileCountryCode": 310,
                                             "carrier": "T-Mobile",
                                             "homeMobileNetworkCode": 260,
                                             "radioType": "WCDMA"},
                           'indoorFlag': True,
                           'wifiJSON': [{"RSSI": -56, "frequency": 5200, "SSID": "Columbia University",
                                         "BSSID": "d8:c7:c8:2d:31",
                                         "timestamp": 54823832},
                                        {"RSSI": -56, "frequency": 5200, "SSID": "eduroam", "BSSID": "d8:c7:c8:2d:31",
                                         "timestamp": 54823832}],
                           'GPSAlt': 0,
                           'GPSLong': 0,
                           'addr_id': 132,
                           'GPSAccu': 0})
    get_now(raw_data)
