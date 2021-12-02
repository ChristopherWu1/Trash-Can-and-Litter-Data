import pandas as pd
import numpy as np
import codecs
import csv
import seaborn as sns
import matplotlib.pyplot as plt
import pandasql as psql
from datetime import datetime, timedelta
import folium
from folium.plugins import MarkerCluster
import json





#clean data to get brough names. QE, BX,MN,BK,SI, QW
def cleanBoroughs(x):
    intial =  x[:2]
    if(intial == 'MN'):
        return 'MANHATTAN'
    elif(intial == 'BK'):
        return 'BROOKLYN'
    elif(intial == 'BX'):
        return 'BRONX'
    elif(intial == 'SI'):
        return 'STATEN ISLAND'
    else:
        return 'QUEENS'
    return intial

#clean coordinates so we can map onto folium
def cleanCoordinates(x):
    coord = x[7:-1]
    splitted = coord.split()
    splitted.reverse()
    return(splitted)

def cleanLiiterBasket(x):
    if x == "Litter Basket / Request":
        return "Litter Basket Request"
    else:
        return x
    
#cleans cans data 
cans = pd.read_csv('DSNY_Litter_Basket_Inventory.csv')
cans['Borough'] = cans['SECTION'].apply(lambda x: cleanBoroughs(x))
#print(cans['borough'][:20])

#group by borough and counts amount of cans
cans_by_borough = cans.groupby('Borough').size().reset_index(name='Counts')
cans_by_borough =  cans_by_borough.sort_values(by=['Counts'], ascending=False)
#print(cans_by_borough)
''' 
recycling_bins = pd.read_csv('Public_Recycling_Bins.csv')
print(recycling_bins[:20])
print(recycling_bins.columns)
'''

'''
#only look at Complaint Type == Litter Basket / Request
litter_complaints = pd.read_csv('litter.csv')
print(litter_complaints[:20])
print(litter_complaints.columns)
'''


# 10 Litter Basket / Request: don't know what that means

#make 311 data and gets population per can and complaint chart
litter_complaints2 = pd.read_csv('311_Service_Requests_from_2010_to_Present.csv')
litter_complaints2.drop(litter_complaints2.loc[litter_complaints2['Complaint Type']== 'Litter Basket Complaint'].index, inplace=True)
'''
print(litter_complaints2[:20])
print(litter_complaints2.columns)
'''
litter_by_borough = litter_complaints2.groupby('Borough').size().reset_index(name='Counts')
litter_by_borough = litter_by_borough.sort_values(by=['Counts'], ascending=False)
#print(litter_by_borough)

population = pd.read_csv('NYC_Population_by_Borough.csv')
population['Borough'] = population['Borough'].apply(lambda x: x.upper())
#print(population)



cans_vs_litter_by_borough = pd.merge(cans_by_borough,litter_by_borough, how = 'inner', on = 'Borough')
cans_vs_litter_by_borough = cans_vs_litter_by_borough.rename(columns={"Counts_x": "Bin Count", "Counts_y": "Litter Complaint Count"})
#print(cans_vs_litter_by_borough)
cans_vs_litter_by_borough.plot(x="Borough", y=["Bin Count", "Litter Complaint Count"], kind="bar")
plt.xticks(fontsize=6, rotation=30)
plt.title("Amount of Trash Cans and Litter Complaints by Borough")
plt.savefig('cans_vs_litter_by_borough.png')
#plt.show()


#make population vs complaint and cans chart

population_vs_cans_litter_by_borough =  pd.merge(cans_vs_litter_by_borough,population, how = 'inner', on = 'Borough')
population_vs_cans_litter_by_borough['People per Bin'] = population_vs_cans_litter_by_borough['Population'] / population_vs_cans_litter_by_borough['Bin Count']
population_vs_cans_litter_by_borough['People per Complaint'] = population_vs_cans_litter_by_borough['Population'] / population_vs_cans_litter_by_borough['Litter Complaint Count']
population_vs_cans_litter_by_borough.plot(x="Borough", y=["People per Bin", "People per Complaint"], kind="bar")
#sns.scatterplot(data = population_vs_cans_litter_by_borough, x="Population", y="People per Complaint", hue="Borough")
#print(population_vs_cans_litter_by_borough)
plt.xticks(fontsize=6, rotation=30)
plt.title("People per Trash Cans and Litter Complaints by Borough")
plt.savefig('population_vs_cans_litter_by_borough.png')
#plt.show()

#compare complaint types
litter_complaints = pd.read_csv('311_Service_Requests_from_2010_to_Present.csv')
litter_complaints['Complaint Type'] = litter_complaints['Complaint Type'].apply(lambda x: cleanLiiterBasket(x))
print(litter_complaints['Complaint Type'].unique())
'''
complaint_type = litter_complaints.groupby('Complaint Type').count()
complaint_type = complaint_type['Unique Key']
'''

complaint_type = litter_complaints['Complaint Type'].value_counts()
df = complaint_type.to_frame().reset_index()
df.rename({'Complaint Type': 'Count', 'index': 'Type'}, axis=1, inplace=True)
print(df)
splot=sns.barplot(x="Type",y="Count",data=df)
plt.xticks(fontsize=6, rotation=0)
plt.title("Types of Complaints")
plt.bar_label(splot.containers[0])
plt.savefig('Types_of_Complaints.png')
#plt.show()



#make folium maps 
baskets = pd.read_csv('DSNY_Litter_Basket_Inventory.csv')
baskets['Coordinate'] = baskets['point'].apply(lambda x: cleanCoordinates(x))
m = folium.Map(location=[40.768731, -73.964915],tiles = 'OpenStreetMap', zoom_start=11, control_scale=True)

marker_cluster = MarkerCluster().add_to(m)
print(baskets['Coordinate'][0],baskets['BASKETID'][0])
for x,y in zip(baskets['Coordinate'], baskets['BASKETID']):
    folium.Marker(location = x , popup = y, icon=folium.Icon(color="blue", icon='trash', prefix = 'fa')).add_to(marker_cluster)
#folium.Marker(location = [40.768731, -73.964915], popup = "Hunter College").add_to(m)
outfp = "base_map.html"
m.save(outfp)



#make folium make that is broken into dsny groups
map_2 = folium.Map(location=[40.768731, -73.964915],tiles = 'OpenStreetMap', zoom_start=11, control_scale=True)
districts = pd.read_csv('DSNY_Sections.csv')
baskets2 = pd.read_csv('DSNY_Litter_Basket_Inventory.csv')
L = baskets2['SECTION'].value_counts()
df = L .to_frame().reset_index()
df.rename({'SECTION': 'COUNT', 'index': 'SECTION'}, axis=1, inplace=True)

count_of_cans_per_district = pd.merge(df,districts, how = 'inner', on = 'SECTION')
sect = json.load(open('DSNY Sections.geojson'))



folium.Choropleth(
geo_data=sect,
data=count_of_cans_per_district,
columns=['SECTION',"COUNT"],
key_on="feature.properties.section",
fill_color='YlGn',
fill_opacity=1,
line_opacity=0.2,
legend_name="Bin Count",
smooth_factor=0,
Highlight= True,
line_color = "#0000",
name = "Trash and Bin Data",
show=False,
overlay=True,
nan_fill_color = "White"
).add_to(map_2)



marker_cluster = MarkerCluster().add_to(map_2)
print(baskets['Coordinate'][0],baskets['BASKETID'][0])
for x,y in zip(baskets['Coordinate'], baskets['BASKETID']):
    folium.Marker(location = x , popup = y, icon=folium.Icon(color="blue", icon='trash', prefix = 'fa')).add_to(marker_cluster)
    
folium.LayerControl().add_to(map_2)
#df = baskets.merge(districts, on = 'SECTION')

outfp = "layer_map.html"
map_2.save(outfp)
