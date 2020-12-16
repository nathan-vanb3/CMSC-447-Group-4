import json
import io
import copy

institutionGeo = {
    'type': 'FeatureCollection',
    'features': []
}

newFeature = {
    'type': 'Feature',

    'geometry': {
        'type': 'Point',
        'coordinates': None
    },

    'properties': {
        'name': None,
    }
}

jsonFile = open('institution_locations.json')
data = json.load(jsonFile)

for feature in data:
    newFeature['properties']['name'] = feature['Canonical Facility Name']
    newFeature['geometry']['coordinates'] = [float(feature['Longitude']), float(feature['Latitude'])]
    institutionGeo['features'].append(copy.deepcopy(newFeature))
    print('done with ' + feature['Canonical Facility Name'])

jsonFile.close()

jsonFile = open('us_institutions_geo.json', 'w')
json.dump(institutionGeo, jsonFile)

