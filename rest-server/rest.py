from flask import (Flask, render_template)
from flask import request
import pymongo
from pymongo import MongoClient
import json

app = Flask(__name__)

# Returns single polygon in JSON format by fips
# def getCoordinateByFips(fips):
#    geoIdDict={}
#    with open("geoJSON.txt", encoding='ISO-8859-1') as f:
#        data = json.load(f)
#    for x in data["features"]:
#        geoIdDict[x["properties"]["GEO_ID"][9:]] = json.dumps(x["geometry"])
#    return geoIdDict[fips]


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
    full_data = {'Canonical Facility Name': facility, 'Pop Tested Positive': pop_positive, 'Pop Deaths': pop_deaths}
    return full_data

@app.route('/county')
# Returns JSON format data with county data 
def getCountyData():
    fips = request.args.get('fips')
    if fips == None:
        return "Error: no fips entered"
    county_data = pullCountyData(fips)
    return json.dumps(county_data)

@app.route('/allcountydata')
# Returns all county case/death data in JSON format
# Format: [{'fips': fips, 'cases': cases. 'deaths': deaths},...,]
def getAllCountyData():
    client = MongoClient('mongodb://databaseUser:CMSC447@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&ssl_cert_reqs=CERT_NONE&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client["Project_447"]
    collection_covid = db["covid_counties"]
    stuff = list(collection_covid.find({},{"_id": 0, "FIPS": 1, "cases": 1, "deaths": 1, "date": 1}))

    sorted_by_date = sorted(stuff, key=lambda i:i['date'], reverse=True)

    lookup = []
    all_data = []
    for stat in sorted_by_date:
        fips = stat["FIPS"]
        if fips not in lookup:
            lookup.append(fips)
            del stat["date"]
            all_data.append(stat)

    return json.dumps(all_data)


@app.route('/facility')
# Returns JSON format data with facility data
def getFacilityData():
    facility = request.args.get('facility')
    if facility == None:
        return "Error: no facility entered"
    facility_data = pullFacilityData(facility)
    return json.dumps(facility_data)

@app.route('/allfacilitydata')
def getAllFacilityData():
    client = MongoClient('mongodb://databaseUser:CMSC447@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&ssl_cert_reqs=CERT_NONE&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client["Project_447"]
    collection_covid = db["covid_jail"]
    stuff = list(collection_covid.find({},{"_id": 0, "Canonical Facility Name": 1, "Pop Tested Positive": 1, "Pop Deaths": 1, "date": 1}))

    sorted_by_date = sorted(stuff, key=lambda i:i['date'], reverse=True)

    lookup = []
    all_data = []
    for stat in sorted_by_date:
        facility = stat["Canonical Facility Name"]
        if facility not in lookup:
            lookup.append(facility)
            del stat["date"]
            all_data.append(stat)

    return json.dumps(all_data)

# @app.route('/allcoordinates')
# Returns all county polygons in JSON format
# def getAllCoordinates():
#    geoIdDict={}
#    with open("geoJSON.txt", encoding='ISO-8859-1') as f:
#        data = json.load(f)
#    for x in data["features"]:
#        geoIdDict[x["properties"]["GEO_ID"][9:]] = json.dumps(x["geometry"])
#    return json.dumps(geoIdDict)

app.run (debug=True)
