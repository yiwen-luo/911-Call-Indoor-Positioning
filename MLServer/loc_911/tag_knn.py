import math
import numpy

WIFI_RSSI_MIN = -100
CELL_RSSI_MIN = -110
WIFI_SCORE_THRESHOLD = 12
CELL_SCORE_THRESHOLD = 7


def knn_loc(tagged_data, current_data):
    # If room number available
    result = knn_wifi_room(tagged_data, current_data)
    if result:
        return result

    # If level number is available
    result = knn_wifi_level(tagged_data, current_data, 2)
    if result:
        return result

    # If building address is avilable
    result = knn_cell_building(tagged_data, current_data)
    if result:
        return result

    return None


def knn_wifi_room(tagged_data, current_data):
    current_wifi = {}
    current_wifi_list = current_data["wifiJSON"]
    for ap in current_wifi_list:
        current_wifi[ap["BSSID"]] = int(ap["RSSI"])

    wifi_score = []
    wifi_score_i = []
    original_i = 0
    for tagged in tagged_data:
        if tagged[8]:
            wifi_score_temp = 0.0
            for ap in tagged[8]:
                if ap["BSSID"] in current_wifi.keys():
                    wifi_score_temp += math.fabs(ap["RSSI"] - current_wifi[ap["BSSID"]])
                else:
                    wifi_score_temp += math.fabs(ap["RSSI"] - WIFI_RSSI_MIN)
            wifi_score_temp /= len(tagged[8])
            if wifi_score_temp <= WIFI_SCORE_THRESHOLD:
                wifi_score.append(wifi_score_temp)
                wifi_score_i.append(original_i)
        original_i += 1

    if wifi_score:
        best_index = numpy.argmin(wifi_score)
        return tagged_data[wifi_score_i[best_index]][11]
    else:
        return None


def knn_wifi_level(tagged_data, current_data, k):
    current_wifi = {}
    current_wifi_list = current_data["wifiJSON"]
    for ap in current_wifi_list:
        current_wifi[ap["BSSID"]] = int(ap["RSSI"])

    wifi_score = []
    for tagged in tagged_data:
        if tagged[8]:
            wifi_score_temp = 0.0
            for ap in tagged[8]:
                if ap["BSSID"] in current_wifi.keys():
                    wifi_score_temp += math.fabs(ap["RSSI"] - current_wifi[ap["BSSID"]])
                else:
                    wifi_score_temp += math.fabs(ap["RSSI"] - WIFI_RSSI_MIN)
            wifi_score_temp /= len(tagged[8])
            wifi_score.append(wifi_score_temp)

    # k is set to 2 in this case
    if len(wifi_score) > 1:
        min_1 = 99999
        min_1_i = 0
        min_2 = 99999
        min_2_i = 0
        for i, score in enumerate(wifi_score):
            if score < min_1:
                min_2 = min_1
                min_2_i = min_1_i
                min_1 = score
                min_1_i = i
            elif score < min_2:
                min_2 = score
                min_2_i = i
    elif len(wifi_score) == 1:
        result = tagged_data[0][11]
        result["room"] = ""
        return result
    else:
        return None

    if tagged_data[min_1_i][11]["floor"] == tagged_data[min_2_i][11]["floor"]:
        result = tagged_data[min_1_i][11]
        result["room"] = ""
        return result
    else:
        return None


def knn_cell_building(tagged_data, current_data):
    current_cell = {}
    current_cell_list = current_data["cellTowerJSON"]["cellTowers"]
    for cell in current_cell_list:
        current_cell[cell["cellId"]] = int(cell["signalStrength"])

    cell_score = []
    cell_score_i = []
    original_i = 0
    for tagged in tagged_data:
        if tagged[9]["cellTowers"]:
            cell_score_temp = 0.0
            for cell in tagged[9]["cellTowers"]:
                if cell["cellId"] in current_cell.keys():
                    cell_score_temp += math.fabs(cell["signalStrength"] - current_cell[cell["cellId"]])
                else:
                    cell_score_temp += math.fabs(cell["signalStrength"] - CELL_RSSI_MIN)
            cell_score_temp /= len(tagged[9]["cellTowers"])
            if cell_score_temp <= CELL_SCORE_THRESHOLD:
                cell_score.append(cell_score_temp)
                cell_score_i.append(original_i)
        original_i += 1

    if cell_score:
        best_index = numpy.argmin(cell_score)
        result = tagged_data[cell_score_i[best_index]][11]
        result["room"] = ""
        result["floor"] = ""
        return result
    else:
        return None
