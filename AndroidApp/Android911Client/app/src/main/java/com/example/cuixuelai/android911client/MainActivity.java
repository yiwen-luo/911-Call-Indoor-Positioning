package com.example.cuixuelai.android911client;

import android.annotation.TargetApi;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.location.Criteria;
import android.location.GpsSatellite;
import android.location.GpsStatus;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.telephony.CellInfo;
import android.telephony.CellInfoCdma;
import android.telephony.CellInfoGsm;
import android.telephony.CellInfoLte;
import android.telephony.CellInfoWcdma;
import android.telephony.SmsManager;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Toast;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;





public class MainActivity extends AppCompatActivity implements SensorEventListener,TaggingFragment.TaggingCommunication, GoogleApiClient.ConnectionCallbacks,
                    GoogleApiClient.OnConnectionFailedListener{

    public static final String TAG = MainActivity.class.getSimpleName();
    //---map realted stuff---
    private GoogleMap mMap;
    private GoogleApiClient mGoogleApiClient;
    private LocationRequest mLocationRequest;
    private com.google.android.gms.location.LocationListener myFusedLocationListener;
    //---wifi---
    private WifiManager wifi;
    private String wifi_data;

    private float millibars_of_pressure = 0;

    //---gps
    private LocationManager locationManager;
    private String provider;
    private GpsStatus gpsStatus;
    private Criteria criteria;
    //gps_json is a global variable that stores the up to date gps info
    private JSONObject gps_json;
    //---cell tower
    private TelephonyManager telophonyManager;
    private List<CellInfo> cellInfoLis;
    private int radioType;
    private String radioTypeString;
    private JSONObject celltower_json;

    //---TAGGED DATA
    private String taggedDataString;
    //---REQUEST DATA
    private String requestDataString;

    //---get estimated response
    private String estimatedLocation = "estimated location";

    //---global location requested from Fused Location Provider
    protected Location mCurrentLocation;

    //---id generator;
    private int request_id = 0;
    private List<Integer> allAddressesIds;
    private HashMap<Integer,List<String>> allAddresses;





    @TargetApi(Build.VERSION_CODES.JELLY_BEAN_MR1)
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // a couple things that needs to be done
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        //initialize locaiton service -----


        mGoogleApiClient = new GoogleApiClient.Builder(this)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .addApi(LocationServices.API)
                .build();


        this.wifi = (WifiManager) getSystemService(Context.WIFI_SERVICE);
        //when wifiReceiver is called
        WifiScanReceiver wifiReceiver = new WifiScanReceiver();

        //----gps initialization
        //----need to open GPS setting here
        this.locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        if (this.locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
            //for debugging
            Toast.makeText(this, "GPS is working", Toast.LENGTH_LONG).show();
        } else {
            Toast.makeText(this, "GPS is not working", Toast.LENGTH_LONG).show();
        }

        this.criteria = new Criteria();
        this.criteria.setAccuracy(Criteria.ACCURACY_FINE);
        this.criteria.setAltitudeRequired(true);
        this.criteria.setBearingRequired(true);
        this.criteria.setCostAllowed(true);
        this.criteria.setPowerRequirement(Criteria.POWER_LOW);
        this.criteria.setSpeedRequired(true);
        this.provider = this.locationManager.getBestProvider(criteria, true);
        //note that if the device doens't know the last-known location, then it should return null
        //not very useful at this point
        Location location_lastknown = locationManager.getLastKnownLocation(provider);
        //toast longitude, altitude here for the moment

        //register locationManager with a listener; on location changed, send the new location to the server
        this.locationManager.requestLocationUpdates(provider, 1000, 0, myLocationListener);
        //gps listener detached for now
        this.locationManager.addGpsStatusListener(statusListener);

        this.gps_json = new JSONObject();
        try {
            this.gps_json.put("latitude", 999);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        try {
            this.gps_json.put("longitude", 999);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        try {
            this.gps_json.put("accuracy", 999);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        try {
            this.gps_json.put("indoor", true);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        try {
            this.gps_json.put("altitude", 999);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        //try to send it for once at here; modify it later
        SensorManager mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        Sensor mPressure = mSensorManager.getDefaultSensor(Sensor.TYPE_PRESSURE);
        mSensorManager.registerListener(this, mPressure, SensorManager.SENSOR_DELAY_UI);

        //----telephony manager initialization
        this.celltower_json = new JSONObject();
        //----telophony manager initialization


        //-----------auto-generated stuff-----------------
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);


        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //Toast.makeText(getApplicationContext(), "clicked floating button", Toast.LENGTH_LONG).show();
                String url = "http://ec2-54-209-70-235.compute-1.amazonaws.com/get_Loc";
                //write a new method to assemble query string
                try {
                    assembleQueryString();
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                new PostGetEstimatedLocationTask().execute(url);
                //textEstimatedAddress("testing");
                Toast.makeText(getApplicationContext(), estimatedLocation, Toast.LENGTH_LONG).show();
                //store estimated location somewhere

                if (!estimatedLocation.equals("estimated location")) {
                    //check if json object'

                    JsonElement root = new JsonParser().parse(estimatedLocation);
                    JsonObject obj = root.getAsJsonObject();
                    //Toast.makeText(getApplicationContext(), obj.get("street").toString(), Toast.LENGTH_SHORT).show();
                    //build a hash map here...
                    int request_id = Integer.parseInt(obj.get("loc_id").toString());
                    List<String> addr = new ArrayList<>();
                    addr.add("Room: " + obj.get("room").toString() + "\tFloor: " + obj.get("floor").toString());
                    addr.add("Building: " + obj.get("building").toString());
                    addr.add("Street1: " + obj.get("street").toString());
                    addr.add("Street2: " + obj.get("city").toString() + " ," + obj.get("state").toString() + " ," + obj.get("zip").toString());

                    allAddresses.put(request_id, addr);
                    //Toast.makeText(getApplicationContext(), allAddresses.toString(), Toast.LENGTH_SHORT).show();

                }

            }
        });
        this.myFusedLocationListener = new com.google.android.gms.location.LocationListener() {
            @Override
            public void onLocationChanged(Location location) {
                mCurrentLocation = location;
                try {
                    handleGoogleLocation();
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        };
        this.mGoogleApiClient = new GoogleApiClient.Builder(this)
                .addApi(LocationServices.API)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .build();


        this.mLocationRequest = LocationRequest.create()
                .setPriority(LocationRequest.PRIORITY_LOW_POWER)
                .setInterval(1000)
                .setFastestInterval(1000);

        this.allAddresses = new HashMap<Integer, List<String>>();


    }

    @Override
    protected void onStart() {
        this.mGoogleApiClient.connect();
        super.onStart();
    }
    @Override
    protected void onStop() {
        this.mGoogleApiClient.disconnect();
        super.onStop();
    }
    @Override
    protected void onResume() {
        super.onResume();
        this.mGoogleApiClient.connect();
    }
    //getCellTower scans cell tower info and return a cell tower JSON
    //only return cell info if matches with radioType
    @TargetApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
    private JSONObject getCellTower() throws JSONException {
        JSONObject cellTowerJSON = new JSONObject();
        this.telophonyManager = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
        String carrier = this.telophonyManager.getNetworkOperatorName();
        String networkOperator = this.telophonyManager.getNetworkOperator();
        int homeMobileCountryCode = -1;
        int homeMobileNetworkCode = -1;

        homeMobileCountryCode = Integer.parseInt(networkOperator.substring(0, 3));
        homeMobileNetworkCode = Integer.parseInt(networkOperator.substring(3));

        cellTowerJSON.put("carrier", carrier);
        cellTowerJSON.put("homeMobileCountryCode", homeMobileCountryCode);
        cellTowerJSON.put("homeMobileNetworkCode", homeMobileNetworkCode);

        //this.celltower_json.put("simOperator", simOperator);
        JSONArray gsm = new JSONArray();
        JSONArray cdma = new JSONArray();
        JSONArray wcdma = new JSONArray();
        JSONArray lte = new JSONArray();
        JSONArray cellTowerObjects = new JSONArray();
        //phone type

        int radioType = this.telophonyManager.getNetworkType();
        String radioTypeString = "I DON'T KNOW";


        switch (radioType){
            //cdma
            case (TelephonyManager.NETWORK_TYPE_1xRTT):{
                radioTypeString = "CDMA";
                break;
            }
            //cdma
            case (TelephonyManager.NETWORK_TYPE_CDMA): {
                radioTypeString = "CDMA";
                break;
            }
            //gsm
            case (TelephonyManager.NETWORK_TYPE_EDGE): {
                radioTypeString = "GSM";
                break;
            }
            //cdma
            case (TelephonyManager.NETWORK_TYPE_EHRPD): {
                radioTypeString = "CDMA";
                break;
            }
            //cdma
            case (TelephonyManager.NETWORK_TYPE_EVDO_0): {
                radioTypeString = "CDMA";
                break;
            }
            //cdma
            case (TelephonyManager.NETWORK_TYPE_EVDO_A): {
                radioTypeString = "CDMA";
                break;
            }
            //cdma
            case (TelephonyManager.NETWORK_TYPE_EVDO_B): {
                radioTypeString = "CDMA";
                break;
            }
            //gsm
            case (TelephonyManager.NETWORK_TYPE_GPRS): {
                radioTypeString = "GSM";
                break;
            }
            //wcdma
            case (TelephonyManager.NETWORK_TYPE_HSDPA): {
                radioTypeString = "WCDMA";
                break;
            }
            //wcdma
            case (TelephonyManager.NETWORK_TYPE_HSPA): {
                radioTypeString = "WCDMA";
                break;
            }
            //wcdma
            case (TelephonyManager.NETWORK_TYPE_HSUPA): {
                radioTypeString = "WCDMA";
                break;
            }
            //gsm
            case (TelephonyManager.NETWORK_TYPE_IDEN): {
                radioTypeString = "GSM";
                break;
            }
            //wcdma
            case (TelephonyManager.NETWORK_TYPE_UMTS): {
                radioTypeString = "WCDMA";
                break;
            }
            //unknown
            case (TelephonyManager.NETWORK_TYPE_UNKNOWN): {
                radioTypeString = "UNKNOWN";
                break;
            }

        }

        //cellTowerJSON.put("radioType", this.radioTypeString);

        List<CellInfo> allCellInfos = this.telophonyManager.getAllCellInfo();

        for (CellInfo temp: allCellInfos) {

            if (temp instanceof CellInfoGsm) {
                if (radioTypeString.equals("GSM")) {
                    //cell id
                    int cid = ((CellInfoGsm) temp).getCellIdentity().getCid();
                    //location area code
                    int lac = ((CellInfoGsm) temp).getCellIdentity().getLac();
                    //mobile country code
                    int mcc = ((CellInfoGsm) temp).getCellIdentity().getMcc();
                    //mobile network code
                    int mnc = ((CellInfoGsm) temp).getCellIdentity().getMnc();
                    //signal strength
                    int dbm = ((CellInfoGsm) temp).getCellSignalStrength().getDbm();
                    //pack data here
                    long timestamp = temp.getTimeStamp();
                    if (cid != Integer.MAX_VALUE) {
                        JSONObject gsm_info = new JSONObject();
                        gsm_info.put("cellId", cid);
                        gsm_info.put("locationAreaCode", lac);
                        gsm_info.put("mobileCountryCode", mcc);
                        gsm_info.put("mobileNetworkCode", mnc);
                        gsm_info.put("signalStrength", dbm);
                        gsm_info.put("timestamp", timestamp);
                        cellTowerObjects.put(gsm_info);
                    }
                }
            } else if (temp instanceof CellInfoCdma) {
                if (radioTypeString.equals("CDMA")) {
                    int basestation_id = ((CellInfoCdma) temp).getCellIdentity().getBasestationId();
                    int latitude = ((CellInfoCdma) temp).getCellIdentity().getLatitude();
                    int longitude = ((CellInfoCdma) temp).getCellIdentity().getLongitude();
                    int network_id = ((CellInfoCdma) temp).getCellIdentity().getNetworkId();
                    int system_id = ((CellInfoCdma) temp).getCellIdentity().getSystemId();
                    //not sure if it's the right signal strength
                    int dbm = ((CellInfoCdma) temp).getCellSignalStrength().getDbm();
                    long timestamp = temp.getTimeStamp();
                    if (basestation_id != Integer.MAX_VALUE) {
                        JSONObject cdma_info = new JSONObject();

                        cdma_info.put("cellId", basestation_id);
                        cdma_info.put("latitude", latitude);
                        cdma_info.put("longitude", longitude);
                        cdma_info.put("network_id", network_id);
                        cdma_info.put("system_id", system_id);
                        cdma_info.put("signalStrength", dbm);
                        cdma_info.put("timestamp", timestamp);
                        cellTowerObjects.put(cdma_info);
                    }
                }

            } else if (temp instanceof CellInfoWcdma) {
                if (radioTypeString.equals("WCDMA")) {
                    int cid = ((CellInfoWcdma) temp).getCellIdentity().getCid();
                    int lac = ((CellInfoWcdma) temp).getCellIdentity().getLac();
                    int mcc = ((CellInfoWcdma) temp).getCellIdentity().getMcc();
                    int mnc = ((CellInfoWcdma) temp).getCellIdentity().getMnc();
                    int psc = ((CellInfoWcdma) temp).getCellIdentity().getPsc();
                    int dbm = ((CellInfoWcdma) temp).getCellSignalStrength().getDbm();
                    long timestamp = temp.getTimeStamp();

                    //cid = INTEGER.MAX_VALUE if unknown
                    if (cid != Integer.MAX_VALUE) {
                        JSONObject wcdma_info = new JSONObject();
                        wcdma_info.put("cellId", cid);
                        wcdma_info.put("locationAreaCode", lac);
                        wcdma_info.put("mobileCountryCode", mcc);
                        wcdma_info.put("mobileNetworkCode", mnc);
                        //wcdma_info.put("psc", psc);
                        wcdma_info.put("signalStrength", dbm);
                        wcdma_info.put("timestamp", timestamp);
                        cellTowerObjects.put(wcdma_info);
                    }
                }

            } else if (temp instanceof CellInfoLte) {
                if (radioTypeString.equals("LTE")) {
                    //do something here
                    int ci = ((CellInfoLte) temp).getCellIdentity().getCi();
                    int mcc = ((CellInfoLte) temp).getCellIdentity().getMcc();
                    int mnc = ((CellInfoLte) temp).getCellIdentity().getMnc();
                    int pci = ((CellInfoLte) temp).getCellIdentity().getPci();
                    int tac = ((CellInfoLte) temp).getCellIdentity().getTac();
                    int timing_advance = ((CellInfoLte) temp).getCellSignalStrength().getTimingAdvance();
                    long timestamp = temp.getTimeStamp();
                    if (ci != Integer.MAX_VALUE) {
                        JSONObject lte_info = new JSONObject();
                        lte_info.put("cellId", ci);
                        lte_info.put("mobileCountryCode", mcc);
                        lte_info.put("mobileNetworkCode", mnc);
                        //lte_info.put("pci", pci);
                        //lte_info.put("tac", tac);
                        lte_info.put("timingAdvance", timing_advance);
                        lte_info.put("timestamp", timestamp);
                        cellTowerObjects.put(lte_info);
                    }
                }
            }
        }
        cellTowerJSON.put("cellTowers", cellTowerObjects);
        cellTowerJSON.put("radioType", radioTypeString);
        //Toast.makeText(getApplicationContext(), cellTowerJSON.toString(), Toast.LENGTH_LONG).show();
        return cellTowerJSON;

    }

    @TargetApi(Build.VERSION_CODES.JELLY_BEAN_MR1)
    private JSONArray getWifi() throws JSONException {
        this.wifi.startScan();
        JSONArray wifiJSON = new JSONArray();
        List<ScanResult> wifiScanList = this.wifi.getScanResults();
        for (int i = 0; i < wifiScanList.size(); i++) {
            JSONObject access_point = new JSONObject();
            String bssid = wifiScanList.get(i).BSSID;
            String ssid = wifiScanList.get(i).SSID;
            int rssi = wifiScanList.get(i).level;
            long timestamp = wifiScanList.get(i).timestamp;
            int frequency = wifiScanList.get(i).frequency;
            access_point.put("SSID", ssid);
            access_point.put("BSSID", bssid);
            access_point.put("RSSI", rssi);
            access_point.put("frequency", frequency);
            wifiJSON.put(access_point);

        }
        return wifiJSON;
    }


    @Override
    public final void onSensorChanged(SensorEvent event) {
        //smooth the data
        this.millibars_of_pressure = (float) (event.values[0] * 0.75 + this.millibars_of_pressure * 0.25);
        //Toast.makeText(getApplicationContext(), Float.toString(this.millibars_of_pressure), Toast.LENGTH_LONG).show();
    }

    @Override
    public final void onAccuracyChanged(Sensor sensor, int accuracy) {
    }


    @Override
    public void passTaggedData(String street1, String zip, String city, String state, String floor, String room, String building) throws JSONException {
        JSONObject tagJSON = new JSONObject();
        JSONObject addressJSON = new JSONObject();
        addressJSON.put("street", street1);
        addressJSON.put("zip", zip);
        addressJSON.put("city", city);
        addressJSON.put("state", state);
        addressJSON.put("floor", floor);
        addressJSON.put("room", room);
        addressJSON.put("building", building);
        tagJSON.put("addrJSON", addressJSON);
        JSONArray wifiJSON = this.getWifi();
        tagJSON.put("wifiJSON", wifiJSON);

        JSONObject cellTowerJSON = this.getCellTower();
        tagJSON.put("cellTowerJSON", cellTowerJSON);
        tagJSON.put("GPSLat", this.gps_json.get("latitude"));
        tagJSON.put("GPSLong", this.gps_json.get("longitude"));
        tagJSON.put("GPSAlt", this.gps_json.get("altitude"));
        tagJSON.put("GPSAccu", this.gps_json.get("accuracy"));

        //tagJSON.put("infoorFlag", this.gps_json.get("indoor"));
        tagJSON.put("indoorFlag", true);

        tagJSON.put("pressure", this.millibars_of_pressure);

        this.taggedDataString = tagJSON.toString();
        String tag_url = "http://ec2-54-209-70-235.compute-1.amazonaws.com/set_TagLoc";
        //Toast.makeText(getApplicationContext(), requestDataString, Toast.LENGTH_LONG).show();
        new PostTaggedDataTask().execute(tag_url);
    }

    public void assembleQueryString() throws JSONException {
        JSONObject requestJSON = new JSONObject();
        JSONArray wifiJSON = this.getWifi();
        requestJSON.put("loc_id", this.request_id);
        this.request_id++;
        requestJSON.put("wifiJSON", wifiJSON);
        JSONObject cellTowerJSON = this.getCellTower();
        requestJSON.put("cellTowerJSON", cellTowerJSON);
        requestJSON.put("GPSLat", this.gps_json.get("latitude"));
        requestJSON.put("GPSLong", this.gps_json.get("longitude"));
        requestJSON.put("GPSAlt", this.gps_json.get("altitude"));
        requestJSON.put("GPSAccu", this.gps_json.get("accuracy"));
        requestJSON.put("indoorFlag", true);
        requestJSON.put("pressure", this.millibars_of_pressure);
        this.requestDataString = requestJSON.toString();
        Log.e(TAG, requestDataString);
        this.textEstimatedAddress(wifiJSON.toString());

    }

    //re-write this part; need to have a new handleGoogleLocation method

    @Override
    public void onConnected(Bundle bundle) {
        Log.i(TAG, "Connected to GoogleApiClient");

        if (this.mCurrentLocation == null) {
            this.mCurrentLocation = LocationServices.FusedLocationApi.getLastLocation(this.mGoogleApiClient);
        }
        //start updating location
        LocationServices.FusedLocationApi.requestLocationUpdates(this.mGoogleApiClient, this.mLocationRequest, this.myFusedLocationListener);
        try {
            handleGoogleLocation();
        } catch (JSONException e) {
            e.printStackTrace();
        }

    }


    @Override
    public void onConnectionSuspended(int i) {

    }



    @Override
    public void onConnectionFailed(ConnectionResult connectionResult) {
        Toast.makeText(getApplicationContext(), "connection failed", Toast.LENGTH_LONG).show();

    }

    private class WifiScanReceiver extends BroadcastReceiver {

        @Override
        public void onReceive(Context context, Intent intent) {
            List<ScanResult> wifiScanList = wifi.getScanResults();
            //actively updating wifi info here if necessary

        }
    }


    private class PostWifiTask extends AsyncTask<String, Integer, String> {

        @Override
        protected String doInBackground(String... params) {
            String url = params[0];
            POST(url, wifi_data);
            //Toast.makeText(getApplicationContext(), wifi_data, Toast.LENGTH_SHORT).show();
            return "Sent Wifi JSON";
        }
    }

    private class PostTaggedDataTask extends  AsyncTask<String, Integer, String> {

        @Override
        protected String doInBackground(String... params) {
            String url = params[0];
            POST(url, taggedDataString);
            return "Sent Tagged Data";
        }
    }

    private class PostGPSTask extends AsyncTask<String, Integer, String> {

        @Override
        protected String doInBackground(String... params) {

//            Toast.makeText(getApplicationContext(), "POSTING GPS DATA", Toast.LENGTH_SHORT).show();
            String url = params[0];
            POST(url, gps_json.toString());
            return "Sent GPS JSON";
        }
    }

    private class PostGetEstimatedLocationTask extends AsyncTask<String, Integer, String> {

        @Override
        protected String doInBackground(String... params) {
            String url = params[0];
            String response = POST(url, requestDataString);
            estimatedLocation = response;
            return "got estimated location!";

        }
    }

    private final GpsStatus.Listener statusListener = new GpsStatus.Listener() {

        @Override
        public void onGpsStatusChanged(int event) {
            gpsStatus = locationManager.getGpsStatus(null);
            switch (event)
            {
                case GpsStatus.GPS_EVENT_STARTED:
                    break;
                case GpsStatus.GPS_EVENT_FIRST_FIX:
                    break;
                case GpsStatus.GPS_EVENT_SATELLITE_STATUS:
                    // need to do something here with the satellite
                    Iterable<GpsSatellite> satellites = gpsStatus.getSatellites();
                    String s_strings = "";
                    int total_satellites = 0;
                    //need to get level of each satellites
                    total_satellites = 0;
                    for (GpsSatellite sat: satellites) {
                        if (sat.getSnr() != 0) {
                            total_satellites ++;
                        }
                    }
                    //Toast.makeText(getApplicationContext(), s_strings, Toast.LENGTH_LONG).show();
                    //seems like if indoor, all snr is 0
                    if(total_satellites >= 1) {
                        try {
                            gps_json.put("indoor", false);
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    } else {
                        try {
                            gps_json.put("indoor", true);
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }

                    String gps_url = "http://ec2-54-209-70-235.compute-1.amazonaws.com/set_GPS";
                    //new PostGPSTask().execute(gps_url);
                    break;
                case GpsStatus.GPS_EVENT_STOPPED:
                    break;
            }
        }
    };
    private LocationListener myLocationListener = new LocationListener(){
        @Override
        public void onLocationChanged(Location location) {
            //update the
            double longitude = location.getLongitude();
            double latitude = location.getLatitude();
            double altitude = location.getAltitude();
            float accuracy = location.getAccuracy();
            try {
                gps_json.put("longitude", longitude);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            try {
                gps_json.put("latitude", latitude);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            try {
                gps_json.put("altitude", altitude);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            try {
                gps_json.put("accuracy", accuracy);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            //Toast.makeText(getApplicationContext(), "My Location Listener " + gps_json.toString(), Toast.LENGTH_LONG).show();
            String gps_url = "http://ec2-54-209-70-235.compute-1.amazonaws.com/set_GPS";
            //new PostGPSTask().execute(gps_url);
            //update the global variable with the given data
        }

        @Override
        public void onStatusChanged(String provider, int status, Bundle extras) {
        }

        @Override
        public void onProviderEnabled(String provider) {

        }

        @Override
        public void onProviderDisabled(String provider) {

        }
    };

    @Override
    protected void onDestroy() {
        super.onDestroy();
        this.locationManager.removeGpsStatusListener(this.statusListener);
    }


    public String POST(String url, String json_string) {
        InputStream inputStream = null;
        String response = "no response";
        try {
            //create HTTP client
            HttpClient httpclient = new DefaultHttpClient();

            //make POST request to the given URL
            HttpPost httpPost = new HttpPost(url);
            //build jsonObject

            //set json to StringEntity
            StringEntity se = new StringEntity(json_string);

            //set httpPost Entity
            httpPost.setEntity(se);
            //set headers to inform server about the type of the co
            httpPost.setHeader("Accept", "application/json");
            httpPost.setHeader("Content-type", "application/json");
            //execute POST request to the given URL
            HttpResponse httpResponse = httpclient.execute(httpPost);
            //receive response as inputStream
            inputStream = httpResponse.getEntity().getContent();

            //convert inputstream to string

            if(inputStream != null) {
                ByteArrayOutputStream result = new ByteArrayOutputStream();
                byte[] buffer = new byte[1024];
                int length;
                while ((length = inputStream.read(buffer)) != -1) {
                    result.write(buffer, 0, length);
                    return result.toString("UTF-8");
                }

            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        return "no response...";

    }
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            //start a new activity for tagging;
            Toast.makeText(getApplicationContext(), "clicked", Toast.LENGTH_SHORT).show();
            Intent in = new Intent(MainActivity.this, TaggingActivity.class);

            in.putExtra("all_address", this.allAddresses);
            startActivity(in);
            return true;
        }
        return super.onOptionsItemSelected(item);
    }


    public void handleGoogleLocation() throws JSONException {
        double currentLatitude = this.mCurrentLocation.getLatitude();
        double currentLogitude = this.mCurrentLocation.getLongitude();
        double currentAltitude = this.mCurrentLocation.getAltitude();
        float currentAccuracy = this.mCurrentLocation.getAccuracy();
        this.gps_json.put("latitude", currentLatitude);
        this.gps_json.put("longitude", currentLogitude);
        this.gps_json.put("altitude", currentAltitude);
        this.gps_json.put("accuracy", currentAccuracy);

        LatLng latLng = new LatLng(currentLatitude, currentLogitude);
        //can use latlng to draw a map;
        //Toast.makeText(getApplicationContext(), "FUSED LOCATION PROVIDER" + this.gps_json.toString(), Toast.LENGTH_LONG).show();
    }

    public void textEstimatedAddress(String result) {
        SmsManager smsManager = SmsManager.getDefault();
        smsManager.sendTextMessage("+13475830283", null, result, null, null);
    }

    private void setupMap() {
        this.mMap.addMarker(new MarkerOptions().position(new LatLng(0, 0)).title("Marker"));
    }


}

