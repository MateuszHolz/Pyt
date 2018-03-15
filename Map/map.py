import folium
import pandas
#Define get colour function to return certain colour (parameter = elevation of mountain)#
def getColour(elevation):
    if elevation < 1000:
        return "green"
    elif elevation < 2500:
        return "orange"
    else:
        return "red"
#Creating lists out of columns of volc.txt file#
l = pandas.read_csv("volc.txt", sep=",")
lats = list(l["LAT"])
lons = list(l["LON"])
elev = list(l["ELEV"])
#Initialize map / feature group objects#
map = folium.Map(location=[], zoom_start=4, tiles="Mapbox Bright")
fgVolcano = folium.FeatureGroup(name="Volcanoes")
fgPopulation = folium.FeatureGroup(name="Population")
#Add circles (d)
for x, y, e in zip(lats, lons, elev):
    fgVolcano.add_child(folium.Circle(location=[x, y], radius=10000, color=getColour(e), fill=True, fill_opacity=0.8, popup="Elevation: %s meters." % e))
#Define colours of countries by their population and add it as a child to fgPopulation FeatureGroup#
fgPopulation.add_child(folium.GeoJson(data=open("world.json", 'r', encoding='utf-8-sig').read(), style_function=lambda x: {'fillColor': 'green' if x['properties']['POP2005'] < 10**7
                                                                                                                else 'orange' if x['properties']['POP2005'] < 10**7*2
                                                                                                                else 'red'}))
#Add fgs to map#
map.add_child(fgVolcano)
map.add_child(fgPopulation)
map.add_child(folium.LayerControl())
#Save the file as Map1.html#
map.save("Map1.html")
