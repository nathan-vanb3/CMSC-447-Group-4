import './App.css';
import React from 'react';
import mapboxgl from 'mapbox-gl';
import ReactMapboxGl, {Layer, Source, Popup} from 'react-mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import testData from './us_counties_test_style.json';
import chroma from 'chroma-js';
import {renderToString} from 'react-dom/server';
import {Statistic, Radio, DatePicker} from 'antd';
import 'antd/dist/antd.css';

mapboxgl.accessToken = 'pk.eyJ1IjoibmF0aGExIiwiYSI6ImNraTlkcDFmaDA2d3Qyem14MnAxMmo4YWcifQ.MNUuilLvnxFLCCjcGqI0WQ';

class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      dataType: 'cases'
    };

    this.toggleData = this.toggleData.bind(this);
  }

  toggleData(type) {
    this.setState({dataType: type});
  }

  render() {
    return(
      <>
        <CovidMap dataType={this.state.dataType}/>
        <DataSwitch toggleData={this.toggleData}/>
        <DateRange/>
      </>
    );
  }
}

class PopupInt extends React.Component {
  render() {
    return(
      <div>
        <h1>{this.props.name}</h1>
        <Statistic value={this.props.deaths} title='County Deaths'/>
        <Statistic value={this.props.cases} title='County Cases'/>
      </div>
    );
  }
}

class DataSwitch extends React.Component {
  onChange = (e) => {
    this.props.toggleData(e.target.value);
    console.log('changed to ' + e.target.value)
  }

  render() {
    return(
      <div className='dataSwitch'>
        <Radio.Group onChange={this.onChange} defaultValue='cases'>
          <Radio.Button value='cases'>Cases</Radio.Button>
          <Radio.Button value='deaths'>Deaths</Radio.Button>
        </Radio.Group>
      </div>
    );
  }
}

class DateRange extends React.Component {
  render() {
    return(
      <div className='datePicker'>
        <DatePicker/>
      </div>
    );
  }
}

const Map = ReactMapboxGl({
  accessToken: 'pk.eyJ1IjoibmF0aGExIiwiYSI6ImNraTlkcDFmaDA2d3Qyem14MnAxMmo4YWcifQ.MNUuilLvnxFLCCjcGqI0WQ'
});

class CovidMap extends React.Component {
  constructor(props) {
    super(props);
    
    this.state = {
      popupEvent: null,
      popupShow: false
    }
  }

  casesScale = chroma.scale('OrRd').classes([0, 500, 1000, 3000, 5000, 10000, 30000, 50000]);
  deathsScale = chroma.scale('PuBu').classes([0, 200, 400, 600, 1000, 2000, 5000, 10000]);

  hoveredID = null

  popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
  });

  showPopup(e, map) {
    // Change the cursor
    map.getCanvas().style.cursor = 'pointer';

    var cases = null;
    var deaths = null;

    testData.forEach((row) => {
      if(row['FIPS'] === e.features[0].properties.FIPS) {
        cases = row['cases'];
        deaths = row['deaths'];
      }
    });

    var popupInt = <PopupInt name={e.features[0].properties.NAME} cases={cases} deaths={deaths}/>

    // Show the popup
    this.popup.setLngLat(e.lngLat)
      .setHTML(renderToString(popupInt))
      .addTo(map);
  }

  hidePopup(map) {
    map.getCanvas().style.cursor = '';
    this.popup.remove();
  }

  getBoundingBox(e) {
    var bounds = {}, coords, latitude, longitude;
    coords = e.features[0].geometry.coordinates[0];

    for (var j = 0; j < coords.length; j++) {
      longitude = coords[j][0];
      latitude = coords[j][1];

      bounds.xMin = bounds.xMin < longitude ? bounds.xMin : longitude;
      bounds.xMax = bounds.xMax > longitude ? bounds.xMax : longitude;
      bounds.yMin = bounds.yMin < latitude ? bounds.yMin : latitude;
      bounds.yMax = bounds.yMax > latitude ? bounds.yMax : latitude;
    }
  
    var returnArray = [[bounds.xMin, bounds.yMin], [bounds.xMax, bounds.yMax]]
    return returnArray;
  }

  onMapLoaded = (map) => {
    this.map = map;

    this.map.on('mousemove', 'countyLayer', (e) => {
      if(e.features.length > 0) {
        if(this.hoveredID) {
          this.map.removeFeatureState({id: this.hoveredID, source: 'countySource', sourceLayer: 'us_counties_geo_shaved-4nakyb'});
        }

        this.hoveredID = e.features[0].id;
        this.map.setFeatureState({id: this.hoveredID, source: 'countySource', sourceLayer: 'us_counties_geo_shaved-4nakyb'}, {id: e.features[0].properties.id});

        this.showPopup(e, this.map);
      }

      else {
        this.hidePopup(this.map);
      }
    });

    this.map.on('mouseleave', 'countyLayer', () => {
      if(this.hoveredID) {
        this.map.removeFeatureState({id: this.hoveredID, source: 'countySource', sourceLayer: 'us_counties_geo_shaved-4nakyb'});
      }

      this.hoveredID = null;

      this.hidePopup(this.map);
    });

    this.map.on('click', 'countyLayer', (e) => {
      this.map.fitBounds(this.getBoundingBox(e), {padding: 50});
    })
  }

  render() {
    var colorExpression = ['match', ['get', 'FIPS']];

    var iterOperation = null;
    if(this.props.dataType === 'cases') {
      iterOperation = (row) => {colorExpression.push(row['FIPS'], this.casesScale(row[this.props.dataType]).hex());}
    }
    else {
      iterOperation = (row) => {colorExpression.push(row['FIPS'], this.deathsScale(row[this.props.dataType]).hex());}
    }

    testData.forEach(iterOperation);

    colorExpression.push('rgba(0,0,0,0)');

    var opacityExpression = ['case', ['==', ['feature-state', 'id'], ['get', 'id']], 1, 0.5]

    return(
      <Map
        style='mapbox://styles/mapbox/light-v10'
        maxBounds={[[-168.398438, 17.978733], [-64.335938, 71.965388]]}
        center={[-96.020508, 38.169114]}
        zoom={[4.1]}
        onStyleLoad={this.onMapLoaded}
      >

        <Source
          id='countySource'
          tileJsonSource={{
            type: 'vector',
            url: 'mapbox://natha1.7fjceup1'
          }}
        />

        <Layer
          id='countyLayer'
          type='fill'
          sourceId='countySource'
          sourceLayer='us_counties_geo_shaved-4nakyb'
          paint={{
            'fill-color': colorExpression,
            'fill-opacity': opacityExpression,
            'fill-outline-color': 'black'
          }}
        />
      </Map>
    );
  }
}

export default App;
