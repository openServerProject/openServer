import json

def setJson(filename, dict):
    fetchedValue = {}
    try:
        with open(filename, 'w') as file:
            fetchedValue = {'type': 'success'}
            file.read(json.dumps(dict))
    except:
        fetchedValue = {'type': 'error'}
    return fetchedValue

def getJson(filename):
    fetchedValue = {}
    try:
        with open(filename, 'r') as file:
            fetchedValue = json.loads(file.read())
    except:
        fetchedValue = {'type': 'error'}
    return fetchedValue