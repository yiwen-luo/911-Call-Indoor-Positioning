package com.example.cuixuelai.android911client;


import android.app.Activity;
import android.app.Fragment;
import android.hardware.SensorEvent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Switch;

import org.json.JSONException;


public class TaggingFragment extends Fragment {
    TaggingCommunication myTaggingCommunication;
    Button tagButton;
    EditText street1;
    EditText zip;
    EditText state;
    EditText city;
    EditText building;
    EditText floor;
    EditText room;
    Switch mySwitch;
    boolean tagging_permission;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        //get edit text by id...

        View view =  inflater.inflate(R.layout.tagging_fragment, container, false);
        this.street1 = (EditText) view.findViewById(R.id.editText_street1);
        this.zip = (EditText) view.findViewById(R.id.editText_Zip);
        this.city = (EditText) view.findViewById(R.id.editText_City);
        this.state = (EditText) view.findViewById(R.id.editText_State);
        this.floor = (EditText) view.findViewById(R.id.editText_Floor);
        this.room = (EditText) view.findViewById(R.id.editText_Room);
        this.building = (EditText) view.findViewById(R.id.editText_Building);
        this.tagging_permission = false;
        this.mySwitch = (Switch) view.findViewById(R.id.switch1);
        mySwitch.setChecked(false);
        mySwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    tagging_permission = true;
                } else {
                    tagging_permission = false;
                }
            }
        });
        this.tagButton = (Button) view.findViewById(R.id.tagging_button);
        this.tagButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //pass data through passTaggedData to main activity
                if (tagging_permission) {
                    try {
                        myTaggingCommunication.passTaggedData(
                                street1.getText().toString(),
                                zip.getText().toString(),
                                city.getText().toString(),
                                state.getText().toString(),
                                floor.getText().toString(),
                                room.getText().toString(),
                                building.getText().toString());
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                }

            }
        });
        return view;

    }

    interface TaggingCommunication {
        void onSensorChanged(SensorEvent event);

        public void passTaggedData(String street1, String zip, String city, String state, String floor, String room, String building) throws JSONException;
    }

    @Override
    public void onAttach(Activity a) {
        super.onAttach(a);
        myTaggingCommunication = (TaggingCommunication) a;


    }










}
