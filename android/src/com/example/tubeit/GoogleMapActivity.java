package com.example.tubeit;

import android.graphics.Color;
import android.os.Bundle;
import android.support.v4.app.FragmentActivity;
import android.view.View;
import android.widget.CheckBox;
import android.widget.Toast;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.GoogleMap.OnCameraChangeListener;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.UiSettings;
import com.google.android.gms.maps.model.CameraPosition;
import com.google.android.gms.maps.model.Circle;
import com.google.android.gms.maps.model.CircleOptions;
import com.google.android.gms.maps.model.LatLng;

public class GoogleMapActivity extends FragmentActivity implements OnCameraChangeListener {
	
    private GoogleMap mMap;
    private UiSettings mUiSettings;
    
    private static final LatLng EDINBURGH = new LatLng(55.9500, -3.1500);
    
    CircleOptions circleOptions = new CircleOptions()
        .center(new LatLng(55.9500, -3.1500))
        .radius(1000) // In meters
    	.strokeWidth(0.5f)
    	.strokeColor(Color.BLACK)
    	.fillColor(Color.RED);
    
    private LatLng mLangLat;
    //private CameraPosition mPosition;
    
    private float zoom;
    private double latitude;
    private double longitude;
    

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_google_map);
        setUpMapIfNeeded();
    }

    @Override
    protected void onResume() {
        super.onResume();
        setUpMapIfNeeded();
    }

    private void setUpMapIfNeeded() {
        if (mMap == null) {
            mMap = ((SupportMapFragment) getSupportFragmentManager().findFragmentById(R.id.map)).getMap();
            if (mMap != null) {
                setUpMap();
            }
        }
    }

    private void setUpMap() {
    	mMap.moveCamera(CameraUpdateFactory.newLatLngZoom(EDINBURGH, 11));
        //mMap.addMarker(new MarkerOptions().position(new LatLng(55.9500, -3.1500)).title("Marker"));

        mMap.setOnCameraChangeListener(this);
        
        mUiSettings = mMap.getUiSettings();   
        
        // Get back the mutable Circle
        Circle circle = mMap.addCircle(circleOptions);
    }
    

    /**
     * Checks if the map is ready (which depends on whether the Google Play services APK is
     * available. This should be called prior to calling any methods on GoogleMap.
     */
    private boolean checkReady() {
        if (mMap == null) {
            Toast.makeText(this, R.string.map_not_ready, Toast.LENGTH_SHORT).show();
            return false;
        }
        return true;
    }

    public void setZoomButtonsEnabled(View v) {
        if (!checkReady()) {
            return;
        }
        // Enables/disables the zoom controls (+/- buttons in the bottom right of the map).
        mUiSettings.setZoomControlsEnabled(((CheckBox) v).isChecked());
    }
    
    @Override
    public void onCameraChange(final CameraPosition mPosition) {
    	
        mLangLat = mPosition.target;
        
        zoom = mPosition.zoom;
        latitude = mLangLat.latitude;
        longitude = mLangLat.longitude;
       
        System.out.println(zoom);
        System.out.println(latitude);
        System.out.println(longitude);
    }

}
