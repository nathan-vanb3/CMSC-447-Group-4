import pymongo
from pymongo import MongoClient

# Pulls the most recent to date deaths and cases for the requested county and state
def pullfromCountyDB(input_county, input_state):
    client = MongoClient('mongodb://Katherine:EYSrHvWmxsiLCmkD@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client["Project_447"]
    collection_covid = db["covid_counties"]
    collection_jail = db["covid_jail"]
    x = collection_covid.find({"county":input_county, "state":input_state},
                              {"_id": 0, "date": 1, "county": 1, "state": 1, "cases": 1, 
                               "deaths": 1}).sort([("date", -1)]).limit(1)
    for data in x:
        print(data)
        
# Enter county and state
pullfromCountyDB("Snohomish", "Washington")

# Pulls the most recent to date deaths and positive numbers for the requested facility and state
def pullfromJailDB(facility, state):
    client = MongoClient('mongodb://Katherine:EYSrHvWmxsiLCmkD@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client["Project_447"]
    collection_covid = db["covid_counties"]
    collection_jail = db["covid_jail"]
    x = collection_jail.find({"Canonical Facility Name": facility, "State": state}, 
                             {"_id": 0, "date": 1, "Canonical Facility Name": 1, "State": 1, "Pop Deaths": 1, 
                              "Pop Tested Positive": 1}).sort([("date", -1)]).limit(1)
    for data in x:
        print(data)

# Enter facility name and state
pullfromJailDB("Shakopee","Minnesota")
