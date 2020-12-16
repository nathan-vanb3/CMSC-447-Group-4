import json
import pandas as pd
import copy
import requests
import io

jsonFile = open('us_counties_geo.json')
data = json.load(jsonFile)

newFeatures = []

idNum = 0;
for p in data['features']:
    template = copy.deepcopy(p)
    template['properties']['FIPS'] = template['properties']['STATE'] + template['properties']['COUNTY']
    template['properties']['NAME'] = template['properties']['NAME'] + ' ' + template['properties']['LSAD']
    template['id'] = idNum
    template['properties']['id'] = idNum
    del template['properties']['COUNTY']
    del template['properties']['STATE']
    del template['properties']['GEO_ID']
    del template['properties']['CENSUSAREA']
    del template['properties']['LSAD']
        
    newFeatures.append(template)
    
    print('done with ' + template['properties']['FIPS'])
    idNum += 1

data['features'] = copy.deepcopy(newFeatures)

jsonFile.close()
jsonFile = open('us_counties_geo_shaved.json', 'w')
json.dump(data, jsonFile)


urlCovidSet = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
urlCovPrison = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSAMWHkg82Nv2abt5CXl7Z_6zfWJY5KZXjo3dnwA83DlkQbKeYKVcePcYqQ7F0F_TkYsGOhhbe3BDGw/pub?gid=19995249&single=true&output=csv'

buffer = requests.get(urlCovidSet).content
countyData = pd.read_csv(io.StringIO(buffer.decode('utf-8')), dtype={'fips':str, 'date':str})

countyData.replace('', 'NaN')

countyData['fips'][countyData.county == 'New York City'] = '99999'

countyData.dropna(inplace=True)

toBeStyled = []

subset = countyData[countyData['date'] == '2020-11-06']

for code in pd.unique(subset['fips']):
    tempDict = {}
    tempDict['FIPS'] = code
    tempDict['cases'] = int(subset[subset['fips'] == code].iloc[0]['cases'])
    tempDict['deaths'] = int(subset[subset['fips'] == code].iloc[0]['deaths'])
    toBeStyled.append(tempDict)
    print('done with ' + code)

jsonFile = open('us_counties_test_style.json', 'w')
json.dump(toBeStyled, jsonFile)
    