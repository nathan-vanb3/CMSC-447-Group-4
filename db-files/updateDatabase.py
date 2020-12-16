import requests
import schedule
import time
from pymongo import MongoClient
urlCovidSet = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
urlCovPrison = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSAMWHkg82Nv2abt5CXl7Z_6zfWJY5KZXjo3dnwA83DlkQbKeYKVcePcYqQ7F0F_TkYsGOhhbe3BDGw/pub?gid=19995249&single=true&output=csv'
infoFile=open('info.csv', 'r', encoding="utf8")
infoLines = infoFile.readlines()[1:]
zipLoc=open('ziploc.csv', 'r')
zipLoc = zipLoc.readlines()[1:]
dictPrison=[]
dictInfo={}
dictInfo2={}
dictZip={}
for line in zipLoc:
    line = line.strip()
    line = line.split(";")
    dictZip[line[0]]=[line[3],line[4]]
for line in infoLines:
    line = line.split(",")
    dictInfo[line[1]]=line[6]
    dictInfo2[line[5]] = line[6]
def updateDB():
    print("Updating Files")
    dictCovid=[]
    dictPrison = []
    r = requests.get(urlCovidSet, allow_redirects=True)
    open('counties_covid_data.csv', 'wb').write(r.content)
    r = requests.get(urlCovPrison, allow_redirects=True)
    open('jail_prison_data.csv', 'wb').write(r.content)
    count = 0
    covid = open('counties_covid_data.csv')
    jail = open('jail_prison_data.csv', encoding="utf8")
    client = MongoClient('mongodb://Richard:xqqMyBFF51KlZgxx@cluster0-shard-00-00.jy5gc.mongodb.net:27017,cluster0-shard-00-01.jy5gc.mongodb.net:27017,cluster0-shard-00-02.jy5gc.mongodb.net:27017/<covid>?ssl=true&replicaSet=atlas-4e1z3x-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client["Project_447"]
    collection_covid = db["covid_counties"]
    collection_jail = db["covid_jail"]
    covidLines = covid.readlines()[1:]
    jailLines = jail.readlines()[1:]
    collection_covid.delete_many({})
    collection_jail.delete_many({})
    print("Starting counties parsing")
    for line in covidLines:
        line = line.split(",")
        line = [elem.strip() for elem in line]
        if line[2] == "New York" and line[1] == "New York City" and line[3]=="":
            post = {"_id": count, "date": line[0], "county": line[1], "state": line[2], "FIPS": "00001",
                    "cases": line[4],
                    "deaths": line[5]}
            dictCovid.append(post)
            count+=1
        elif line[3]!="":
            post = {"_id": count, "date": line[0], "county": line[1], "state": line[2], "FIPS": line[3],
                    "cases": line[4],
                    "deaths": line[5]}
            dictCovid.append(post)
            count += 1
    count = 0
    print("Starting jail parsing")
    for line in jailLines:
        line = line.split(",")
        if dictInfo.get(line[3]) != None and dictInfo2.get(line[2]) != None:
            if dictZip.get(dictInfo.get(line[3])) != None:
                if not line[4].isdigit():
                    line[4] = None
                else:
                    line[4] = int(line[4])
                if not line[5].isdigit():
                    line[5] = 0
                else:
                    line[5] = int(line[5])
                if not line[6].isdigit():
                    line[6] = None
                else:
                    line[6] = int(line[6])
                if not line[7].isdigit():
                    line[7] = 0
                else:
                    line[7] = int(line[7])
                post = {"_id": count, "date": line[0], "State": line[2], "Canonical Facility Name": line[3],
                        "Pop Tested": line[4], "Pop Tested Positive": line[5], "Pop Tested Negative": line[6],
                        "Pop Deaths": line[7], "Latitude": dictZip[dictInfo[line[3]]][0],
                        "Longitude": dictZip[dictInfo[line[3]]][1]}
                dictPrison.append(post)
                count += 1
    print("inserting documents")
    collection_jail.insert_many(dictPrison, ordered=False)
    collection_covid.insert_many(dictCovid,ordered=False)
    print("Done updating!")
updateDB()
schedule.every().day.at("23:59").do(updateDB)
while 1:
    print("Waiting")
    schedule.run_pending()
    time.sleep(60)
