import json

#Method retrieves information from filename
def readFileInfo(filename):

    with open(filename, "r") as file:
        fileInfo = json.load(file)
        file.close()
    
    return fileInfo

#Method writes information to filename
def writeFileInfo(filename, information):

    with open(filename, "w") as file:
        json.dump(information, file)