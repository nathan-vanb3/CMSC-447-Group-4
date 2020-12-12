import pandas as pd
import requests
import io

urlCovidSet = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
urlCovPrison = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSAMWHkg82Nv2abt5CXl7Z_6zfWJY5KZXjo3dnwA83DlkQbKeYKVcePcYqQ7F0F_TkYsGOhhbe3BDGw/pub?gid=19995249&single=true&output=csv'

buffer = requests.get(urlCovidSet).content
countyData = pd.read_csv(io.StringIO(buffer.decode('utf-8')), dtype={'fips':str, 'date':str})

countyData.replace('', 'NaN')

countyData['fips'][countyData.county == 'New York City'] = '99999';

countyData.dropna(inplace=True);

toBeImported = {}

for code in pd.unique(countyData['fips']):
    subset = countyData[countyData['fips'] == code]
    countyName = subset[]
    for date in pd.unique(countyData['date']):
        if(subset[subset['date' == date]].empty):
            subset.append({'fips': code, })
    print('done ' + code)
    