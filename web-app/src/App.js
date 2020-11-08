import React from 'react';
import ReactDOMServer from 'react-dom/server';
import './App.css';
import {Switch, DatePicker} from 'antd';
import {MapContainer, GeoJSON, LayersControl} from 'react-leaflet';
import countyBounds from './merged.json';
import Choropleth from 'react-leaflet-choropleth';
import chroma from 'chroma-js';

console.log(countyBounds);

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      toggled: false,
    }

    this.toggleData = this.toggleData.bind(this);
  }

  toggleData() {
    this.state.toggled ? this.setState({toggled: false}) : this.setState({toggled: true});
  }

  render() {
    return(
      <div id='rootGrid'>
        <MapObject dataToggled={this.state.toggled}/>
        <DatePickerObject />
      </div>
    );
  }
}

class DataToggle extends React.Component {
  render() {
    return(
      <div id='dataToggle'>
        <Switch checkedChildren='Deaths' unCheckedChildren='Cases' onClick={this.props.toggle}/>
      </div>
    );
  }
}

function DatePickerObject() {
  const {RangePicker} = DatePicker;

  return(
    <div id='datePicker'>
      <RangePicker />
    </div>
  );
}

class Popup extends React.Component {
  render() {
    return(
      <div>
        <p>{this.props.feature.properties.NAME} {this.props.feature.properties.LSAD}</p>
        <p>{this.props.feature.properties.deaths}</p>
        <p>{this.props.feature.properties.cases}</p>
      </div>
    );
  }
}

class MapObject extends React.Component {
  getColorDeaths(string) {
    var colorSpace = chroma.scale(['white', 'red']);
    var convertedInt = string / 7157;

    return colorSpace(convertedInt).hex();
  }

  getColorCases(string) {
    var colorSpace = chroma.scale(['white', 'blue']);
    var convertedInt = string / 317727;

    return colorSpace(convertedInt).hex();
  }

  casesElement = <GeoJSON data={countyBounds} style={(feature) => {
    return {fillColor: this.getColorCases(feature.properties.cases), weight: 1, color: 'grey', fillOpacity: 1};
  }} onEachFeature={(feature, layer) => {
    var content = ReactDOMServer.renderToString(<Popup feature={feature} />)
    layer.bindPopup(content);
  }}/>

  deathsElement = <GeoJSON data={countyBounds} style={(feature) => {
    return {fillColor: this.getColorDeaths(feature.properties.deaths), weight: 1, color: 'grey', fillOpacity: 1};
  }} onEachFeature={(feature, layer) => {
    var content = ReactDOMServer.renderToString(<Popup feature={feature} />)
    layer.bindPopup(content);
  }}/>

  render() {
    return(
      <MapContainer id='mapObject' center={[39.82, -98.58]} zoom={5} bounds={[[50, -125], [25, -67]]} zoomSnap={0}>
        <LayersControl position='topright'>
          <LayersControl.BaseLayer checked name='Deaths'>
            {this.deathsElement}
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer checked name='Cases'>
            {this.casesElement}
          </LayersControl.BaseLayer>
        </LayersControl>
      </MapContainer>
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
