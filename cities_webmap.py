import os

import folium
import pandas as pd
from branca.utilities import split_six

# Pathing to and reading in the csv with city names, longitudes, latitudes, population etc to a pandas df
city_data_path = os.path.join('data', 'us-cities.csv')
city_df = pd.read_csv(city_data_path)

population_column = city_df['population']

# filepath for geojson which contains coordinate info for mapping state boundaries on map
states_geo = os.path.join('data', 'us-states.json')

# Pathing to and reading in .csv with states and populations as name, pop
state_data_path = os.path.join('data', 'us-state-populations.csv')
state_df = pd.read_csv(state_data_path)

threshold_scale = split_six(state_df['pop'])

# Median of lat/lon used to center the map between the data points
mean_latitude = city_df['lat'].mean()
mean_longitude = city_df['lon'].mean()

# Finding min/max of populations for generating quartiles
minimum_population = population_column.min()
maximum_population = population_column.max()

# Creating the base folium map centered on the mean lat/lon
base_map = folium.Map(location=[mean_latitude, mean_longitude], tiles='Mapbox Control Room',
                      zoom_start=5)

# Identifying quartiles for setting a green to red color gradient based on population
lower_quartile = int(population_column.quantile(.25))
second_quartile = int(population_column.median())
third_quartile = int(population_column.quantile(.75))


def set_marker_color(population):
    """ Returns a color str based on relative population for city markers """
    if population in range(minimum_population, lower_quartile):
        color = 'lightgreen'
    elif population in range(lower_quartile, second_quartile):
        color = 'green'
    elif population in range(second_quartile, third_quartile):
        color = 'orange'
    else:
        color = 'darkred'
    return color


# Feature group to hold all the city markers on the base map
city_fg = folium.FeatureGroup(name='50 Most Populous US Cities')


for population, latitude, longitude, name, rank in zip(city_df['population'], city_df['lat'], city_df['lon'],
                                                       city_df['place'], city_df['rank']):
    formatted_population = "{:,}".format(population)
    # Adding one marker per city on the map with a population color and XY coords
    city_fg.add_child(
        folium.Marker(location=[latitude, longitude], popup=f'#{rank}, {name}, Population: {formatted_population}',
                      icon=folium.Icon(
                          color=set_marker_color(population))))

# Adding the feature group to the base map once all markers have been added
base_map.add_child(city_fg)

# Reading oceans.json which has polygon details for the world oceans
oceans_data_path = os.path.join('data', 'oceans.json')
# Applying the geojson info to the map, defaults to a blue color to resemble water
base_map.add_child(folium.GeoJson(
    data=open(oceans_data_path, 'r', encoding='utf-8-sig').read(), name='Oceans'))

# Adding choropleth which is the gradient of overall state population
base_map.choropleth(
    geo_data=states_geo,
    name='State Population Choropleth',
    data=state_df,
    columns=['name', 'pop'],
    key_on="feature.properties.name",
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='US Population Per State (Census 2017)',
    threshold_scale=threshold_scale,
)

# Adding a series of tile layers which are like map themes. Colors, looks etc
tile_layers = ['OpenStreetMap', 'Mapbox Bright',
               'Stamen Toner', 'Stamen Watercolor']
for layer in tile_layers:
    base_map.add_child(folium.TileLayer(layer))

# Adding the layer control which allows you to choose the current tile layer and features
base_map.add_child(folium.LayerControl())
base_map.add_child(folium.LatLngPopup())
# Generating a usable folium map from all the feature groups and controls
base_map.save('Webmap.html')
