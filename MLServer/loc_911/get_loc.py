# This package is developed by Yiwen Luo (yiwen.luo@columbia.edu)

import tag_knn
import tag_database
import api_baro
import api_geopy
import api_google

DATABASE_SEARCH_RADIUS = 0.001


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

    output: address dictionary

    """

    cell_data = raw_data["cellTowerJSON"]

    # Get data from GPS
    gps_lat = float(raw_data["GPSLat"])
    gps_lng = float(raw_data["GPSLong"])

    # Get data from tagged database, barometer data/API
    tagged_data = tag_database.get_tagged(gps_lat, gps_lng, DATABASE_SEARCH_RADIUS)
    knn_result = tag_knn.knn_loc(tagged_data, raw_data)
    if knn_result:
        if knn_result["floor"]:
            return knn_result
        else:
            baro_floor = str(api_baro.get_floor(gps_lat, gps_lng, raw_data["pressure"]))
            knn_result["floor"] = baro_floor
            return knn_result

    # Get data from Google API, Geopy, and barometer data/API
    google_result = api_google.google_location(
        cell_data["homeMobileCountryCode"],
        cell_data["homeMobileNetworkCode"],
        cell_data["radioType"].lower(),
        cell_data["carrier"],
        cell_data["cellTowers"],
        raw_data["wifiJSON"])
    if google_result:
        geopy_result = api_geopy.get_address(google_result[0], google_result[1])
        if geopy_result:
            result = parse_geopy(geopy_result)
            baro_floor = str(api_baro.get_floor(gps_lat, gps_lng, raw_data["pressure"]))
            result["floor"] = baro_floor
            return result

    # If everything failed
    geopy_result = api_geopy.get_address(gps_lat, gps_lng)
    if geopy_result:
        return parse_geopy(geopy_result)
    else:
        print "Temporarily no data available"
        return {"building": "", "city": "", "room": "", "zip": "", "floor": "", "state": "", "street": ""}


def parse_geopy(geopy_result):
    geopy_result = geopy_result.split(",")
    result = {}
    result["building"] = geopy_result[0].strip()
    result["city"] = geopy_result[6].strip()
    result["room"] = ""
    result["zip"] = geopy_result[8].strip()
    result["floor"] = ""
    result["state"] = geopy_result[5].strip()
    result["street"] = geopy_result[1].strip() + " " + geopy_result[2].strip()
    return result


# for testing only
if __name__ == "__main__":
    raw_data = {
        "wifiJSON": [{"SSID": "Columbia University", "BSSID": "d8:c7:c8:42:dc:41", "RSSI": -67, "frequency": 2412},
                     {"SSID": "BayesRules", "BSSID": "00:1e:e5:83:01:8f", "RSSI": -51, "frequency": 2437},
                     {"SSID": "LabROSA", "BSSID": "00:1e:2a:77:10:be", "RSSI": -60, "frequency": 2437},
                     {"SSID": "701 CEPSR 5GHz", "BSSID": "a4:2b:b0:e9:89:54", "RSSI": -71, "frequency": 5765},
                     {"SSID": "eduroam", "BSSID": "d8:c7:c8:42:dc:52", "RSSI": -62, "frequency": 5180},
                     {"SSID": "Grover (lab)", "BSSID": "10:0d:7f:74:c5:68", "RSSI": -58, "frequency": 2462},
                     {"SSID": "701 CEPSR", "BSSID": "a4:2b:b0:e9:89:55", "RSSI": -64, "frequency": 2412},
                     {"SSID": "Columbia U Secure", "BSSID": "d8:c7:c8:42:dc:50", "RSSI": -64, "frequency": 5180},
                     {"SSID": "eduroam", "BSSID": "d8:c7:c8:42:dc:42", "RSSI": -64, "frequency": 2412},
                     {"SSID": "Columbia U Secure", "BSSID": "d8:c7:c8:42:dc:40", "RSSI": -64, "frequency": 2412},
                     {"SSID": "7LW1 CEPSR", "BSSID": "48:d7:05:f0:36:6e", "RSSI": -65, "frequency": 2412},
                     {"SSID": "speechlab", "BSSID": "00:12:17:0b:0a:4a", "RSSI": -64, "frequency": 2417},
                     {"SSID": "SECE", "BSSID": "00:23:69:5b:4c:38", "RSSI": -80, "frequency": 2462},
                     {"SSID": "Yeah Baby, Yeah!", "BSSID": "f0:99:bf:0c:82:b2", "RSSI": -73, "frequency": 2437},
                     {"SSID": "DVMMWIFI", "BSSID": "20:4e:7f:49:89:d3", "RSSI": -71, "frequency": 2422},
                     {"SSID": "711_5GHz", "BSSID": "10:fe:ed:40:a4:26", "RSSI": -85, "frequency": 5785},
                     {"SSID": "7LW1 CEPSR 5GHz", "BSSID": "48:d7:05:f0:36:6f", "RSSI": -83, "frequency": 5805},
                     {"SSID": "Grover Slow (lab)", "BSSID": "10:0d:7f:74:c5:67", "RSSI": -85, "frequency": 5765},
                     {"SSID": "Yeah Baby, Yeah!", "BSSID": "f0:99:bf:0c:82:b3", "RSSI": -87, "frequency": 5745},
                     {"SSID": "DVMMLab1", "BSSID": "58:6d:8f:1f:6c:30", "RSSI": -83, "frequency": 2437},
                     {"SSID": "Columbia University", "BSSID": "d8:c7:c8:42:dc:51", "RSSI": -63, "frequency": 5180},
                     {"SSID": "Columbia University", "BSSID": "ac:a3:1e:86:be:d0", "RSSI": -92, "frequency": 5805},
                     {"SSID": "711_2.4GHz", "BSSID": "10:fe:ed:40:a4:25", "RSSI": -61, "frequency": 2462},
                     {"SSID": "eduroam", "BSSID": "d8:c7:c8:42:2d:22", "RSSI": -75, "frequency": 2412},
                     {"SSID": "", "BSSID": "80:ea:96:ed:48:98", "RSSI": -78, "frequency": 2462},
                     {"SSID": "PSL Conference Room", "BSSID": "68:7f:74:be:5a:39", "RSSI": -81, "frequency": 2437},
                     {"SSID": "eduroam", "BSSID": "ac:a3:1e:86:be:d2", "RSSI": -89, "frequency": 5805},
                     {"SSID": "eduroam", "BSSID": "d8:c7:c8:42:dd:d2", "RSSI": -93, "frequency": 5745},
                     {"SSID": "Grinspun Labs", "BSSID": "60:33:4b:e3:9c:cd", "RSSI": -89, "frequency": 2412},
                     {"SSID": "CGUI", "BSSID": "98:fc:11:5c:24:da", "RSSI": -87, "frequency": 2432},
                     {"SSID": "Columbia U Secure", "BSSID": "d8:c7:c8:42:dd:d0", "RSSI": -95, "frequency": 5745},
                     {"SSID": "Columbia University", "BSSID": "d8:c7:c8:42:dd:d1", "RSSI": -93, "frequency": 5745},
                     {"SSID": "Costa Conf.", "BSSID": "90:72:40:15:86:c6", "RSSI": -74, "frequency": 2462},
                     {"SSID": "6lw5", "BSSID": "c0:c1:c0:3e:02:d6", "RSSI": -84, "frequency": 2462},
                     {"SSID": "ShareLink-707", "BSSID": "00:12:5f:11:a7:c8", "RSSI": -80, "frequency": 2427},
                     {"SSID": "CongoAir", "BSSID": "60:33:4b:e7:94:9f", "RSSI": -88, "frequency": 2457}],
        "cellTowerJSON": {"carrier": "T-Mobile",
                          "homeMobileCountryCode": 310,
                          "homeMobileNetworkCode": 260,
                          "cellTowers": [{"cellId": 183577101, "locationAreaCode": 52178, "mobileCountryCode": 310,
                                          "mobileNetworkCode": 260, "signalStrength": -87, "timestamp": 9245813623913}],
                          "radioType": "WCDMA"},
        "GPSLat": 40.8094,
        "GPSLong": -73.9609,
        "GPSAlt": 999,
        "GPSAccu": 1000,
        "indoorFlag": True,
        "pressure": 997.521728515625}
    get_now(raw_data)
