import folium
import json
import os
from folium.plugins import BoatMarker


def popupBoat(inName, inSpeed = 0., inHeading = 0., inTws = 0., inRank = 0, inDist = 0.):
    """"
    Sets up the popup to be shown when boatMarker is clicked
    """

    upperName = str.upper(inName)

    line0 = f"{upperName} <br>"
    line1 = f"Rank : {inRank} <br> <br>"
    line2 = f"Heading : {inHeading} <br>"
    line3 = f"Boat Speed: {inSpeed} <br>" 
    line4 = f"Tws : {inTws} <br>"
    line5 = f"Dist. to end : {inDist}"

    htmlPopup = line0 + line1 + line2 + line3 + line4 + line5

    iframe = folium.IFrame(htmlPopup, width=230, height=170)
    popup = folium.Popup(iframe, max_width=230)    

    return popup

with open('/home/tom/Bureau/Developpement/Git/RoboatMap/configFile.JSON','r') as configf :
    configData = json.load(configf)

archivedDirectoryPath = configData["archivedDirectoryPath"]
lastKnownInfosDirectoryPath = configData["lastKnownInfosDirectoryPath"]
foliumMapDirectoryPath = configData["foliumMapDirectoryFile"]

archivedFileSuffix = configData["archivedBoatInfoSuffix"]
boatFileExtension = configData["boatInfoFileExtension"]

fleetList = configData["fleetList"]
fleetColor = configData["fleetColor"]

boatCoords = {}
boatHeading = {}
boatLastInfos = {}

boatsFeatureGroup ={}


for boatName in fleetList :
    listCoords = []
    boatsFeatureGroup[boatName] = folium.FeatureGroup(name = boatName)

    archivedBoatFilePath = os.path.join(archivedDirectoryPath, boatName + archivedFileSuffix + boatFileExtension)
    lastInfosBoatFilePath = os.path.join(lastKnownInfosDirectoryPath, boatName + boatFileExtension)

    with open(archivedBoatFilePath, 'r') as archivedJSON :
        boatInfos = json.load(archivedJSON)
    
    with open(lastInfosBoatFilePath, 'r') as lastJson :
        lastInfos = json.load(lastJson)
    
    for elem in boatInfos[3:] :
        listCoords.append([elem["lat"],elem["lon"]])
        boatHeading[boatName] = elem["heading"]

    boatCoords[boatName] = listCoords

    boatLastInfos[boatName] = lastInfos[0]

my_map = folium.Map(location = boatCoords[fleetList[0]][-1], zoom_start = 5)

for i,boatName in enumerate(boatCoords.keys()):
    
    feature_group = boatsFeatureGroup[boatName]

    boatPolyline = folium.PolyLine(boatCoords[boatName][:], color = fleetColor[i])

    popup = popupBoat(boatName,
                    boatLastInfos[boatName]["speed"],
                    boatLastInfos[boatName]["heading"],
                    boatLastInfos[boatName]["tws"],
                    boatLastInfos[boatName]["rank"],
                    boatLastInfos[boatName]["distanceToEnd"])

    boatOnMap = BoatMarker(boatCoords[boatName][-1], popup = popup, heading=boatHeading[boatName], color = fleetColor[i]).add_to(feature_group)

    boatPolyline.add_to(feature_group)
    feature_group.add_to(my_map)    

folium.LayerControl().add_to(my_map)

my_map.save(foliumMapDirectoryPath)
