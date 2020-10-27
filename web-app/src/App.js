import React from 'react';
import './App.css';
import {Switch, DatePicker} from 'antd';
import {Map, GeoJSON} from 'react-leaflet';
import {BasemapLayer, FeatureLayer} from 'react-esri-leaflet/v2';
import countyBounds from './gz_2010_us_050_00_20m.json';

function App() {
  return(
    <div id='rootGrid'>
      <MapObject />
      <DataToggle />
      <DatePickerObject />
    </div>
  );
}

function DataToggle() {
  return(
    <div id='dataToggle'>
      <Switch checkedChildren='Deaths' unCheckedChildren='Cases'/>
    </div>
  );
}

function DatePickerObject() {
  const {RangePicker} = DatePicker;

  return(
    <div id='datePicker'>
      <RangePicker />
    </div>
  );
}

class MapObject extends React.Component {
  geoJSONStyle = {
    color: 'gray',
    fillColor: 'white',
    opacity: .7,
    fillOpacity: .3
  };

  render() {
    return(
      <Map id='mapObject' center={[39.82, -98.58]} zoom={5}>
        <BasemapLayer name='Gray'/>
        <FeatureLayer url='https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Special_Land_Use_Areas/MapServer/1'/>
        <GeoJSON data={countyBounds} style ={this.geoJSONStyle}/>
      </Map>
    );
  }
}

function Tooltip() {
  return(
    <div>
      <p>Placeholder Tooltip</p>
    </div>
  );
}

export default App;
