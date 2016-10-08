from flask import Flask, render_template, request, jsonify, url_for, redirect, make_response, Response, current_app
from application import db, application
#from .models import *
from .forms import *
import ast, time, json

from loc_911 import get_loc

@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])


def index():
	form1 = EnterDBInfo(request.form)
	form2 = RetrieveDBInfo(request.form)

	if request.method == 'POST' and form1.validate():
		data_entered = User(username=form1.dbNotes.data)
		if (User.query.filter_by(username=form1.dbNotes.data).count() == 1): # username already in db
			uid = User.query.filter_by(username=form1.dbNotes.data)[0].id
		else: # add this username as a new entry
			try:
				db.session.add(data_entered)
				db.session.commit()
				uid = User.query.filter_by(username=form1.dbNotes.data)[0].id
				db.session.close()
			except:
				db.session.rollback()
		return render_template('thanks.html', name=form1.dbNotes.data, user_id=uid)

	if request.method == 'POST' and form2.validate():
		try:
			num_return = int(form2.numRetrieve.data)
			query_db = User.query.order_by(User.id.desc()).limit(num_return)
			for q in query_db:
				print(q.notes)
			db.session.close()
		except:
			db.session.rollback()
		return render_template('results.html', results=query_db, num_return=num_return)
	return render_template('index.html', form1=form1, form2=form2)

@application.route("/set_address_web/<user_id>", methods=['GET', 'POST'])
def set_address_web(user_id):
	form = EnterAddrInfo(request.form)
	if request.method == 'POST' and form.validate():
		#addr = Address(user_id, form.room.data, form.floor.data, form.building.data, form.district.data, form.city.data, form.state.data)
		addr = Address(form.room.data, form.floor.data, form.building.data, form.district.data, form.city.data, form.state.data)
		try:
			db.session.add(addr)
			db.session.commit()
			db.session.close()
		except:
			db.session.rollback()
		return redirect(url_for('get_address_web'))
	return render_template('set_address.html', form=form, user_id=user_id)

@application.route("/get_address_web", methods=['GET', 'POST'])
def get_address_web():
	query_db = Address.query
	return render_template('results.html', results=query_db, num_return=10)


@application.route('/set_address', methods=['GET','POST'])
def set_address():
	params = request.get_json()
	# json object
	data = Address(params)
	try:
		db.session.add(data)
		db.session.commit()
		db.session.close
	except:
		db.session.rollback()
	return Response(status=204)
	

@application.route("/get_address", methods=['GET', 'POST'])
def get_address():
	query_db = Address.query
	return jsonify(data = [i.serialize for i in query_db.all()])


@application.route('/set_CellTower2G', methods=['GET', 'POST'])
def set_CellTower2G():
	params = request.get_json()
	data = CellTower2G(params)
	try:
		db.session.add(data)
		db.session.commit()
		db.session.close
	except:
		db.session.rollback()
	return Response(status=204)

@application.route("/get_CellTower2G", methods=['GET', 'POST'])
def get_CellTower2G():
	query_db = GPSLoc.query
	return jsonify(CellTower2G = [i.serialize for i in query_db.all()])

@application.route('/set_CellTowerWCDMA', methods=['GET', 'POST'])
def set_CellTowerWCDMA():
	params = request.get_json()
	data = CellTowerWCDMA(params)
	try:
		db.session.add(data)
		db.session.commit()
		db.session.close
	except:
		db.session.rollback()
	return Response(status=204)

@application.route("/get_CellTowerWCDMA", methods=['GET', 'POST'])
def get_CellTowerWCDMA():
	query_db = GPSLoc.query
	return jsonify(CellTowerWCDMA = [i.serialize for i in query_db.all()])

#BEGIN--------------------Android data endpoints--------------------	

@application.route('/set_wifiAccessPoints', methods=['GET', 'POST'])
def set_wifiAccessPoints():
	params = request.get_json()
	# json list
	for p in params:
		data = WifiAccessPoints(p)
		try:
			db.session.add(data)
			db.session.commit()
			db.session.close
		except:
			db.session.rollback()
	return Response(status=204)

@application.route("/get_wifiAccessPoints", methods=['GET', 'POST'])
def get_wifiAccessPoints():
	query_db = WifiAccessPoints.query
	return jsonify(wifiAccessPoints = [i.serialize for i in query_db.all()])

@application.route('/set_GPS', methods=['GET', 'POST'])
def set_GPS():
	params = request.get_json()
	# json object
	data = GPSLoc(params)
	try:
		db.session.add(data)
		db.session.commit()
		db.session.close()
	except:
		db.session.rollback()
	return Response(status=204)

@application.route("/get_GPS", methods=['GET', 'POST'])
def get_GPS():
	query_db = GPSLoc.query
	return jsonify(GPS = [i.serialize for i in query_db.all()])

@application.route('/set_CellTower', methods=['GET', 'POST'])
def set_CellTower():
	params = request.get_json()

	wcdmaArray = params['wcdma']
	for w in wcdmaArray:
		wcdma = CellTowerWCDMA(w)
		try:
			db.session.add(wcdma)
			db.session.commit()
			db.session.close()
		except:
			db.session.rollback()
	gsmArray = params['gsm']
	for g in gsmArray:
		gsm = CellTower2G(g)
		try:
			db.session.add(gsm)
			db.session.commit()
			db.session.close()
		except:
			db.session.rollback()

	params['wcdma'] = json.dumps(params['wcdma'])
	params['gsm'] = json.dumps(params['gsm'])
	params['lte'] = json.dumps(params['lte'])
	params['cdma'] = json.dumps(params['cdma'])

	ct = CellTower(params)
	try:
		db.session.add(ct)
		db.session.commit()
		db.session.close()
	except:
		db.session.rollback()
	return Response(status=204)

@application.route('/set_TagLoc', methods=['GET', 'POST'])
def set_TagLoc():
	params = request.get_json()
	if 'addrJSON' in params:
		# json object
		addr = Address(params['addrJSON'])
		try:
			db.session.add(addr)
			db.session.commit()
		except:
			db.session.rollback()
		params['addr_id'] = addr.id	
		# dump json object back to a string
		params['addrJSON'] = json.dumps(params['addrJSON'])
	if 'wifiJSON' in params:
		wifis = params['wifiJSON']
		# json list
		for p in wifis:
			wifi = WifiAccessPoints(p)
			try:
				db.session.add(wifi)
				db.session.commit()
			except:
				db.session.rollback()
		params['wifiJSON'] = json.dumps(params['wifiJSON'])
	if 'cellTowerJSON' in params:
		#wcdmaArray = params['cellTowerJSON']
		params['cellTowerJSON'] = json.dumps(params['cellTowerJSON'])
	params['timestamp'] = time.time()
	tag = TagLoc(params)
	try:
		db.session.add(tag)
		db.session.commit()
		db.session.close()
	except:
		db.session.rollback()

	return Response(status=204)

@application.route("/get_TagLoc", methods=['GET', 'POST'])
def get_TagLoc():
	query_db = TagLoc.query
	return jsonify(TagLoc = [i.serialize for i in query_db.all()])

#END--------------------Android data endpoints--------------------	

#START------------------ REST FLOOR PREDICTIONS ------------------

@application.route('/predict_indoors', methods=['POST'])
def predict_indoors():
	"""
	Predicts indoors vs outdoors

	Sample input:
		Array of objects like:
		{
	    "time": 1456676060,
	    "gpsSpeed": 1.07,
	    "gpsCourse": 272.4609375,
	    "gpsAccuracyVert": 4,
	    "gpsAccuracyHor": 5,
	    "alt": 0,
	    "altPressure": 101.1752
	  	}

	 Sample output:
	 	{
		  "confidence": 1,
		  "location": "indoors"
		}

	"""
	# extract request json
	device_readings_json = request.get_json()

	# make predictions
	predictor = current_app.floor_predictor
	try:
		predictions = predictor.classify_in_out(device_readings_json)

		# return predictions json
		return jsonify(predictions)
	except Exception as e:
		return jsonify({'error':e})

@application.route('/predict_floor_model_1', methods=['POST'])
def predict_floor_model_1():
	"""
	Predicts floor heights for all significant elevation changes in the given timeseries

	Sample input:
		Array of objects like:
		{
	    "time": 1456676060,
	    "gpsSpeed": 1.07,
	    "gpsCourse": 272.4609375,
	    "gpsAccuracyVert": 4,
	    "gpsAccuracyHor": 5,
	    "alt": 0,
	    "altPressure": 101.1752
	  	}

	Sample Output:
		{'end_alt': 10.269609570181514, 
		'start_alt': -0.79593578972263079, 
		'direction': 'up', 
		'floor': 4.0, 
		'start_time': 1456676060, 
		'end_time': 1456676184
		}

	"""
	# extract request json
	device_readings_json = request.get_json()
	
	try:
		# make predictions
		predictor = current_app.floor_predictor
		predictions, df, indoor_ranges = predictor.fit(device_readings_json)

		#pull only the last floor pred
		predictions = sorted(predictions, key=lambda pred: pred['end_time'])
		prediction = {}
		if len(predictions) > 0:
			prediction = predictions[-1]

		# return predictions json
		return jsonify(prediction)
	except Exception as e:
		return jsonify({'error': e})
#END------------------ REST FLOOR PREDICTIONS ------------------


@application.route('/set_floor_data', methods=['GET', 'POST'])
def set_floor_data():
	json = request.get_json()
	for point in json:
		test = False
		if 'test' in point:
			test = bool(point['test'])
		latitude = None
		if 'latitude' in point:
			latitude = point['latitude']
		longitude = None
		if 'longitude' in point:
			longitude = point['longitude']
		log = Floordata(
			time=point['time'],
			gpsSpeed=point['gpsSpeed'],
			gpsCourse=point['gpsCourse'],
			gpsAccuracyVert=point['gpsAccuracyVert'],
			gpsAccuracyHor=point['gpsAccuracyHor'],
			alt=point['alt'],
			altPressure=point['altPressure'],
			deviceId = point['deviceId'],
			latitude = latitude,
			longitude = longitude,
			test=test
		)
		try:
			db.session.add(log)
			db.session.commit()
			db.session.close
		except:
			db.session.rollback()
	return Response(status=204)

@application.route('/get_floor_data', methods=['GET', 'POST'])
def get_floor_data():
	device_id = request.args.get('device_id') or False
	include_test = str_to_bool(request.args.get('test_data') or "False")
	query_db = Floordata.query.filter_by(test=include_test)
	if device_id:
		query_db = query_db.filter_by(deviceId=device_id)
	print query_db.order_by('-id').first().time
	return jsonify(data = [i.serialize for i in query_db.all()])

@application.route('/get_device_ids', methods=['GET'])
def get_device_ids():
	query = db.session.query(Floordata.deviceId.distinct().label("deviceId"))
	ids = [row.deviceId for row in query.all()]
	return jsonify({'ids': ids})

def str_to_bool(s):
	if s == 'True':
		 return True
	elif s == 'False':
		 return False
	else:
		 raise ValueError # evil ValueError that doesn't tell you what the wrong value wa

@application.route('/delete_floor_data', methods=['GET'])
def delete_floor_data():
	device_id = request.args.get('device_id') or False
	if device_id:
		query_db = Floordata.query.filter_by(deviceId=device_id)
		try:
			db.session.delete(query_db)
			db.session.commit()
			db.session.close
		except:
			db.session.rollback()
	return Response(status=204)

#--------------------request handler--------------------	
#make a POST request

@application.route('/get_Loc', methods=['GET', 'POST'])
def get_Loc():
	params = request.get_json()
	if 'wifiJSON' in params:
		wifis = params['wifiJSON']
		# json list
		for p in wifis:
			wifi = WifiAccessPoints(p)
			try:
				db.session.add(wifi)
				db.session.commit()
			except:
				db.session.rollback()
		params['wifiJSON'] = json.dumps(params['wifiJSON'])
	if 'cellTowerJSON' in params:
		#wcdmaArray = params['cellTowerJSON']
		params['cellTowerJSON'] = json.dumps(params['cellTowerJSON'])
	params['timestamp'] = time.time()
	tag = TagLoc(params)
	try:
		db.session.add(tag)
		db.session.commit()
		db.session.close()
	except:
		db.session.rollback()

	response = get_loc.get_now(params)
	#response = str(response)
	return response

#--------------------error handler--------------------

@application.errorhandler(400)
def bad_request(error):
	message = {
			'status': 400,
			'message': 'Bad Request: ' + request.data,
	}
	resp = jsonify(message)
	resp.status_code = 400
	return resp

@application.errorhandler(404)
def not_found(error):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp
