from application import db
from sqlalchemy.inspection import inspect
from sqlalchemy.schema import Index
import time

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key = True)
    room = db.Column(db.Text)
    floor = db.Column(db.Integer)
    building = db.Column(db.Text)
    street = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip = db.Column(db.Text)

    @property
    def serialize(self):
        table = inspect(Address)
        to_return = {}
        for column in table.c:
            field = str(column).split(".")[1]
            to_return[field] = getattr(self, field)
        return to_return

    def __init__(self, params):
        for key, value in params.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return '%s fl:%d room:%s %s %s %s %s %s' % (self.street, self.floor, self.room, self.building, self.district, self.city, self.state, self.zip)

#BEGIN--------------------Android data schema--------------------

class WifiAccessPoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    SSID = db.Column(db.Text) #access point name
    BSSID = db.Column(db.Text) #mac addr
    RSSI = db.Column(db.Integer)
    frequency = db.Column(db.Float) #channel
    timestamp = db.Column(db.Float)

    @property
    def serialize(self):
        table = inspect(WifiAccessPoints)
        to_return = {}
        for column in table.c:
            field = str(column).split(".")[1]
            to_return[field] = getattr(self, field)
        return to_return

    def __init__(self, params):
        for key, value in params.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return '<WifiAccessPoints %r>' % self.SSID

class GPSLoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    altitude = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    indoor = db.Column(db.Boolean)
    timestamp = db.Column(db.Float)

    @property
    def serialize(self):
        table = inspect(GPSLoc)
        to_return = {}
        for column in table.c:
            field = str(column).split(".")[1]
            to_return[field] = getattr(self, field)
        return to_return

    def __init__(self, params):
        for key, value in params.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return '<GPSLoc lat: %r long: %r>' % (self.latitude, self.longitude)


class TagLoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float)
    indoorFlag = db.Column(db.Boolean)
    GPSLat = db.Column(db.Float)
    GPSLong = db.Column(db.Float)
    GPSAlt = db.Column(db.Float)
    GPSAccu = db.Column(db.Float)

    pressure = db.Column(db.Float)
    wifiJSON = db.Column(db.Text)
    cellTowerJSON = db.Column(db.Text)
    addr_id = db.Column(db.Integer, db.ForeignKey('addresses.id'))
    addrJSON = db.Column(db.Text)

    index = db.Index("long_lat", "GPSLat", "GPSLong")

    @property
    def serialize(self):
        table = inspect(TagLoc)
        to_return = {}
        for column in table.c:
            field = str(column).split(".")[1]
            to_return[field] = getattr(self, field)
        return to_return

    def __init__(self, params):
        for key, value in params.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return '<Tag location %s>' % (str(self.addrJson))

#END--------------------Android data schema--------------------
class Floordata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Numeric(precision='16', scale='5'))
    gpsSpeed = db.Column(db.Numeric(precision='18', scale='14'))
    gpsCourse = db.Column(db.Numeric(precision='18', scale='14'))
    gpsAccuracyVert = db.Column(db.Numeric(precision='18', scale='14'))
    gpsAccuracyHor = db.Column(db.Numeric(precision='18', scale='14'))
    alt = db.Column(db.Numeric(precision='18', scale='14'))
    altPressure = db.Column(db.Numeric(precision='18', scale='14'))
    deviceId = db.Column(db.Text)
    latitude = db.Column(db.Numeric(precision='18', scale='14'))
    longitude = db.Column(db.Numeric(precision='18', scale='14'))
    test = db.Column(db.Boolean)

    @property
    def serialize(self):
        return {
            'time' : self.time,
			'gpsSpeed' : self.gpsSpeed,
            'gpsCourse' : self.gpsCourse,
            'gpsAccuracyVert' : self.gpsAccuracyVert,
			'gpsAccuracyHor' : self.gpsAccuracyHor,
            'alt' : self.alt,
			'altPressure' : self.altPressure,
			'longitude' : self.longitude,
			'latitude' : self.latitude
			}
	def __init__(self, time=None, gpsSpeed=None, gpsCourse=None, gpsAccuracyVert=None, gpsAccuracyHor=None, alt=None, altPressure=None, deviceId=None, latitude=None, longitude=None, test=False):
		self.time = time
		self.gpsCourse = gpsCourse
		self.gpsSpeed = gpsSpeed
		self.gpsAccuracyVert = gpsAccuracyVert
		self.gpsAccuracyHor = gpsAccuracyHor
		self.alt = alt
		self.altPressure = altPressure
		self.deviceId = deviceId
		self.latitude = latitude
		self.longitude = longitude
		self.test = test
		def __repr__(self):
			return '<Data %r>' % self.alt
