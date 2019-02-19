import os

import folium
import pandas as pd
from branca.utilities import split_six

city_data_path = os.path.join('data', 'us-cities.csv')
city_df = pd.read_csv(city_data_path)

population_column = city_df['population']

states_geo = os.path.join('data', 'us-states.json')

state_data_path = os.path.join('data', 'us-state-populations.csv')
state_df = pd.read_csv(state_data_path)

threshold_scale = split_six(state_df['pop'])

mean_latitude = city_df['lat'].mean()
mean_longitude = city_df['lon'].mean()

minimum_population = population_column.min()
maximum_population = population_column.max()

base_map = folium.Map(location=[mean_latitude, mean_longitude], tiles='Mapbox Control Room',
                      zoom_start=5)

lower_quartile = int(population_column.quantile(.25))  # Using pandas quantile() to get 1st quartile
second_quartile = int(population_column.median())  # Using pandas quantile() to get 2nd quartile
third_quartile = int(population_column.quantile(.75))  # Using pandas quantile() to get 3rd quartile


def set_marker_color(population):
    if population in range(minimum_population, lower_quartile):
        color = 'lightgreen'
    elif population in range(lower_quartile, second_quartile):
        color = 'green'
    elif population in range(second_quartile, third_quartile):
        color = 'orange'
    else:
        color = 'darkred'
    return color


city_fg = folium.FeatureGroup(name='50 Most Populous US Cities')

for population, latitude, longitude, name, rank in zip(city_df['population'], city_df['lat'], city_df['lon'],
                                                       city_df['place'], city_df['rank']):
    formatted_population = "{:,}".format(population)
    city_fg.add_child(
        folium.Marker(location=[latitude, longitude], popup=f'#{rank}, {name}, Population: {formatted_population}',
                      icon=folium.Icon(
                          color=set_marker_color(population))))

base_map.add_child(city_fg)
oceans_data_path = os.path.join('data', 'oceans.json')
base_map.add_child(folium.GeoJson(data=open(oceans_data_path, 'r', encoding='utf-8-sig').read(), name='Oceans'))

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

tile_layers = ['OpenStreetMap', 'Mapbox Bright', 'Stamen Toner', 'Stamen Watercolor']
for layer in tile_layers:
    base_map.add_child(folium.TileLayer(layer))

base_map.add_child(folium.LayerControl())
base_map.add_child(folium.LatLngPopup())
base_map.save('Webmap.html')
