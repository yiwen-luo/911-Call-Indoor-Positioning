import ast
import json
import mysql.connector
import credential_file


def get_tagged(gps_lat, gps_lng, search_rad):
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
        # 0:id, 1:timestamp, 2:indoor_flag, 3:GPS_latitude, 4:GPS_longitude, 5:GPS_altitude, 6:GPS_accuracy, 7:pressure,
        # 8:list_of_Wifi, 9:cell_towers, 10:address_id, 11:address_dict,

        tag_data.append(
            [cursor_tuple[0], cursor_tuple[1], cursor_tuple[2], cursor_tuple[3], cursor_tuple[4], cursor_tuple[5],
             cursor_tuple[6], cursor_tuple[7], ast.literal_eval(cursor_tuple[8]), json.loads(cursor_tuple[9]),
             cursor_tuple[10], json.loads(cursor_tuple[11])])

    cursor.close()
    cnx.close()

    return tag_data


# for test only
if __name__ == "__main__":
    get_tagged(0, 0, 1000)
