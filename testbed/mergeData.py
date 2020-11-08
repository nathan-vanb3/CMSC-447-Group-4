import json
import pandas as pd

jsonFile = open('gz_2010_us_050_00_20m.json')
data = json.load(jsonFile)

csvFile = pd.read_csv('us-counties.csv', dtype={'fips' : str}, parse_dates=['date'])
csvFile.replace('', 'NaN')
csvFile.dropna()

maxDeaths = 0
maxCases = 0

for p in data['features']:

    subset = csvFile[csvFile['fips'] == (p['properties']['STATE'] + p['properties']['COUNTY'])]

    if subset.empty != True:
        p['properties']['deaths'] = int(subset[subset['date'] == subset['date'].max()]['deaths'])
        p['properties']['cases'] = int(subset[subset['date'] == subset['date'].max()]['cases'])

        if p['properties']['deaths'] > maxDeaths:
            maxDeaths = p['properties']['deaths']

        if p['properties']['cases'] > maxCases:
            maxCases = p['properties']['cases']

jsonFile.close()

jsonFile = open('merged.json', 'w')
json.dump(data, jsonFile)

print(maxDeaths)
print(maxCases)