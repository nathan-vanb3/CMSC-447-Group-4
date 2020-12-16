from flask import (Flask, render_template)
from flask import request
from flask import json
import pymongo
from pymongo import MongoClient

app = Flask(__name__)

# Pulls data from the MongoDB database based on the county
def pullCountyData(input_fips):
    client = MongoClient('mongodb://databaseUser:CMSC447@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&ssl_cert_reqs=CERT_NONE&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client["Project_447"]
    collection_covid = db["covid_counties"]
    collection_info = collection_covid.find({"FIPS": input_fips}, 
            {"date": 1, "FIPS": 1,"cases": 1, "deaths": 1}).sort([("date", -1)]).limit(1)
    
    data = collection_info[0]
    date = data['date']
    cases = data['cases']
    deaths = data['deaths']
    fips = data['FIPS']
    full_data = {'FIPS': fips, 'cases': cases, 'deaths': deaths}
    
    return full_data

def pullCountyDataTemporal(input_date):
    client = MongoClient('mongodb://databaseUser:CMSC447@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&ssl_cert_reqs=CERT_NONE&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    countydb = client['Project_447']['covid_counties']
    allCounties = countydb.find({'date': input_date}, {'FIPS': 1, 'cases': 1, 'deaths': 1, '_id': 0})
    return list(allCounties)
    

# Pulls data from the MongoDB database based on the facility
def pullFacilityData(input_facility):
    client = MongoClient('mongodb://databaseUser:CMSC447@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&ssl_cert_reqs=CERT_NONE&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client["Project_447"]
    collection_jail = db["covid_jail"]
    collection_info = collection_jail.find({"Canonical Facility Name": input_facility}, 
                             {"_id": 0, "date": 1, "Canonical Facility Name": 1, "State": 1, "Pop Deaths": 1, 
                              "Pop Tested Positive": 1}).sort([("date", -1)]).limit(1)

    data = collection_info[0]
    facility = data['Canonical Facility Name']
    state = data['State']
    date = data['date']
    pop_positive = data['Pop Tested Positive']
    pop_deaths = data['Pop Deaths']
    full_data = {'Canonical Facility Name': facility, 'Pop Tested Positive': pop_positive, 'Pop Deaths': pop_deaths, 'date': date}
    return full_data

def pullFacilityDataTemporal(input_date):
    client = MongoClient('mongodb://databaseUser:CMSC447@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&ssl_cert_reqs=CERT_NONE&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    facilitydb = client['Project_447']['covid_jail']

    pipeline = [
        {
            '$group': {
                '_id': {'date': '$date', 'Canonical Facility Name': '$Canonical Facility Name'},
                'name': {'$first': "$Canonical Facility Name"},
                'cases': {'$sum': '$Pop Tested Positive'},
                'deaths': {'$sum': '$Pop Deaths'},
                'date': {'$first': '$date'}
            }
        },
        {
             '$match': {
                'date': input_date
            }
        },
        {
             '$project': {
                '_id': 0,
                'date': 0
            }
        }
    ]

    allFacilities = facilitydb.aggregate(pipeline)
    return list(allFacilities)

def getValidDates():
    client = MongoClient('mongodb://databaseUser:CMSC447@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&ssl_cert_reqs=CERT_NONE&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    countydb = client["Project_447"]["covid_counties"]
    return list(countydb.distinct('date'))

@app.route('/listDates')
def listDates():
    data = getValidDates()
    response = app.response_class(response=json.dumps(data), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route('/county')
# Returns JSON format data with county data 
def getCountyData():
    fips = request.args.get('fips')
    if fips == None:
        return "Error: no fips entered"
    county_data = pullCountyData(fips)
    return county_data

@app.route('/allcountydata')
# Format: [{'FIPS': fips, 'cases': cases. 'deaths': deaths},...,]
def getAllCountyData():
    input_date = request.args.get('date')
    if input_date == None:
        return "Error: no date entered"
    
    client = MongoClient('mongodb://databaseUser:CMSC447@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&ssl_cert_reqs=CERT_NONE&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client["Project_447"]
    collection_covid = db["covid_counties"]
    county_data = collection_covid.find({"date": input_date},{"_id": 0, "FIPS": 1, "cases": 1, "deaths": 1})

    #sorted_by_date = sorted(stuff, key=lambda i:i['date'], reverse=True)
    all_data = []
    for data in county_data:
        fips = data['FIPS']
        cases = data['cases']
        deaths = data['deaths']
        full_data = {'FIPS' : fips, 'cases': cases, 'deaths':deaths}
        all_data.append(full_data)
    return json.dumps(all_data)

@app.route('/countyDataTemporal')
def getCountyDataTemporal():
    date = request.args.get('date')
    if date == None:
        return "Error: no date entered"

    data = pullCountyDataTemporal(date)
    response = app.response_class(response=json.dumps(data), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
    
@app.route('/facilityDataTemporal')
def getFacilityDataTemporal():
    date = request.args.get('date')
    if date == None:
        return "Error: no date entered"

    data = pullFacilityDataTemporal(date)
    response = app.response_class(response=json.dumps(data), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route('/facility')
# Returns JSON format data with facility data
def getFacilityData():
    facility = request.args.get('facility')
    if facility == None:
        return "Error: no facility entered"
    facility_data = pullFacilityData(facility)
    return json.dumps(facility_data)

@app.route('/allfacilitydata')
# Format: [{'name': name, 'cases': cases. 'deaths': deaths},...,]
def getAllFacilityData():
    input_date = request.args.get('date')
    if input_date == None:
        return "Error: no date entered"
   
    client = MongoClient('mongodb://databaseUser:CMSC447@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&ssl_cert_reqs=CERT_NONE&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client["Project_447"]
    collection_covid = db["covid_jail"]
    jail_data = collection_covid.find({"date": input_date},{"_id": 0, "Canonical Facility Name": 1, "Pop Tested Positive": 1, "Pop Deaths": 1})

    all_data = []
    for data in jail_data:
        name = data['Canonical Facility Name']
        cases = data['Pop Tested Positive']
        deaths = data['Pop Deaths']
        full_data = {'name' : name, 'cases': cases, 'deaths':deaths}
        all_data.append(full_data)
 
    return json.dumps(all_data)

app.run (debug=True)
