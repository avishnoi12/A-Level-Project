import json


def readJson(filename):
    #reading the json file
    jsonFile = open(filename,"r")
    obj = json.loads(jsonFile.read())
    return obj

def setJson(filename, keys, value):
    obj = readJson(filename)
    temp = obj
    for key in (keys):
        temp = temp[key]
        print(temp)
    temp = value
    jsonFile = open(filename, "w")
    json.dump(obj, jsonFile, indent = 2) #writing new settings to json file
    jsonFile.close()

setJson("test.json", ("options","Running"), True)