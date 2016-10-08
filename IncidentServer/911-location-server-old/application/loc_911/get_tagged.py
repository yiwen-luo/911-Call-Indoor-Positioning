import ast
import json
import mysql.connector
import credential_file


def from_db(gps_lat, gps_lng, search_rad):
    cnx = mysql.connector.connect(user=credential_file.database_user,
                                  password=credential_file.database_pswd,
                                  host=credential_file.database_addr,
                                  database=credential_file.database_name)
    cursor = cnx.cursor()
    query = ("SELECT * FROM tag_loc T WHERE T.GPSLat>" + str(gps_lat - search_rad) + " AND T.GPSLat<" + str(
        gps_lat + search_rad) + " AND T.GPSLong>" + str(gps_lng - search_rad) + " AND T.GPSLong<" + str(
        gps_lng + search_rad))
    cursor.execute(query)

    tag_data = []
    for cursor_tuple in cursor:
        # 0:id, 1:timestamp, 2:indoor_flag, 3:list_of_Wifi, 4:cell_towers, 5:address_id, 6:address_dict,
        # 7:GPS_accuracy, 8:GPS_altitude, 9:GPS_latitude, 10:GPS_longitude, 11:pressure
        tag_data.append([cursor_tuple[0], cursor_tuple[1], cursor_tuple[2], ast.literal_eval(cursor_tuple[3]),
                         json.loads(cursor_tuple[4]), cursor_tuple[5], cursor_tuple[7],
                         cursor_tuple[8], cursor_tuple[9], cursor_tuple[10], cursor_tuple[11]])

    cursor.close()
    cnx.close()

    return tag_data


if __name__ == "__main__":
    from_db(0, 0, 1000)
