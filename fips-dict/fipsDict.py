import json
def getFipsCoordinate(fips): #return coordinates in json format
    geoIdDict={}
    with open("geojson.txt") as f:
        data=json.load(f)
    for x in data["features"]:
        geoIdDict[x["properties"]["GEO_ID"][9:]]=json.dumps(x["geometry"])
    return fips
