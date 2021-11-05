import pandas as pd
import requests
import json
import cbsodata
import geopandas as gpd
from shapely.geometry.multipolygon import MultiPolygon
import shapely.wkt
import folium
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title = 'Dashboard CO2-uitstoot en woningdichtheid', layout = 'wide')

if st.sidebar.selectbox('Kies een pagina: ', ['co2 kaarten', 'woningdichtheid kaarten']) == 'co2 kaarten':

    geo_co2_merge_2017 = pd.read_csv('geo_co2_merge_2017.csv')
    geo_co2_merge_2018 = pd.read_csv('geo_co2_merge_2018.csv')
    geo_co2_merge_2019 = pd.read_csv('geo_co2_merge_2019.csv')
    
    geo_year = [geo_co2_merge_2017, geo_co2_merge_2018, geo_co2_merge_2019]
    
    with open('geo_co2_merge_2017.json', encoding = "ISO-8859-1") as geofile:
        geo_co2_merge_2017_json = json.load(geofile) 
    with open('geo_co2_merge_2018.json', encoding = "ISO-8859-1") as geofile:
        geo_co2_merge_2018_json = json.load(geofile) 
    with open('geo_co2_merge_2019.json', encoding = "ISO-8859-1") as geofile:
        geo_co2_merge_2019_json = json.load(geofile) 

    geojson_year = [geo_co2_merge_2017_json, geo_co2_merge_2018_json, geo_co2_merge_2019_json]

    dfs_year = pd.DataFrame({'year': [2017, 2018, 2019]})
    dfs_year['geojson_year'] = dfs_year['year'].apply(lambda x: geojson_year[x-2017])
    dfs_year['geo_year'] = dfs_year['year'].apply(lambda x: geo_year[x-2017])

    fig = go.Figure()

    c = 0

    for i, j, k in zip(dfs_year.year, dfs_year.geojson_year, dfs_year.geo_year):
        if c == 0:
            v = True # In eerste instantie is alleen 2017 zichtbaar
        else:
            v = False

        fig.add_trace(go.Choroplethmapbox(geojson=j, locations = k['Gemeenten'],
                                          z = k['totaal_co2'],
                                          colorscale='Oranges',
                                          zmin=k['totaal_co2'].min(),
                                          zmax=k['totaal_co2'].max(),
                                          marker_opacity=0.8, marker_line_width=0.5, marker_line_color = 'orange',
                                          name = i, visible = v,
                                          featureidkey="properties.statnaam",
                                          colorbar={"title": 'CO₂-uitstoot (in ton)'}))
        c += 1


    # Create and add slider
    steps = []
    year_start = 2017
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)}],  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        active=True,
        currentvalue={"prefix": "Jaar: "},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )

    # Update de layout van de kaart
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=5.8, mapbox_center = {"lat": 52.0893191, "lon": 5.1101691})

    # Edit slider labels
    fig['layout']['sliders'][0]['currentvalue']['prefix']='Jaar: '
    for i, jaar in enumerate([2017, 2018, 2019], start = 0):
        fig['layout']['sliders'][0]['steps'][i]['label']=jaar

    # Zet de margins
    fig.update_layout(margin={"r":0, "t": 50, "l": 20, "b": 100},
                      title = 'Totaal bekende CO₂-uitstoot per gemeente<br>(aardgas, elektr., stadswarmte woningen, voertuigbrandstoffen)',
                      title_x = 0.5,
                      title_y = 0.97,
                      font_family = "Calibri Light",
                      title_font_size = 18)

    st.plotly_chart(fig) # Laat de plot zien

    fig = go.Figure()

    c = 0

    for i, j, k in zip(dfs_year.year, dfs_year.geojson_year, dfs_year.geo_year):
        if c == 0:
            v = True # In eerste instantie is alleen 2017 zichtbaar
        else:
            v = False

        fig.add_trace(go.Choroplethmapbox(geojson=j, locations = k['Gemeenten'],
                                          z = k['totaal_co2'],
                                          colorscale='Oranges',
                                          zmin=k['totaal_co2'].min(),
                                          zmax=k['totaal_co2'].max(),
                                          marker_opacity=0.8, marker_line_width=0.5, marker_line_color = 'orange',
                                          name = i, visible = v,
                                          featureidkey="properties.statnaam",
                                          colorbar={"title": 'CO₂-uitstoot (in ton)'}))
        c += 1


    # Create and add slider
    steps = []
    year_start = 2017
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)}],  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        active=True,
        currentvalue={"prefix": "Jaar: "},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )

    # Update de layout van de kaart
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=5.8, mapbox_center = {"lat": 52.0893191, "lon": 5.1101691})

    # Edit slider labels
    fig['layout']['sliders'][0]['currentvalue']['prefix']='Jaar: '
    for i, jaar in enumerate([2017, 2018, 2019], start = 0):
        fig['layout']['sliders'][0]['steps'][i]['label']=jaar

    # Zet de margins
    fig.update_layout(margin={"r":0, "t": 50, "l": 20, "b": 100},
                      title = 'Totaal bekende CO₂-uitstoot per gemeente<br>(aardgas, elektr., stadswarmte woningen, voertuigbrandstoffen)',
                      title_x = 0.5,
                      title_y = 0.97,
                      font_family = "Calibri Light",
                      title_font_size = 18)

    st.plotly_chart(fig) # Laat de plot zien

    fig = go.Figure()

    c = 0

    for i, j, k in zip(dfs_year.year, dfs_year.geojson_year, dfs_year.geo_year):
        if c == 0:
            v = True # In eerste instantie is alleen 2017 zichtbaar
        else:
            v = False

        fig.add_trace(go.Choroplethmapbox(geojson=j, locations = k['Gemeenten'],
                                          z = k['totaal_co2'],
                                          colorscale='Oranges',
                                          zmin=k['totaal_co2'].min(),
                                          zmax=k['totaal_co2'].max(),
                                          marker_opacity=0.8, marker_line_width=0.5, marker_line_color = 'orange',
                                          name = i, visible = v,
                                          featureidkey="properties.statnaam",
                                          colorbar={"title": 'CO₂-uitstoot (in ton)'}))
        c += 1


    # Create and add slider
    steps = []
    year_start = 2017
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)}],  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        active=True,
        currentvalue={"prefix": "Jaar: "},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )

    # Update de layout van de kaart
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=5.8, mapbox_center = {"lat": 52.0893191, "lon": 5.1101691})

    # Edit slider labels
    fig['layout']['sliders'][0]['currentvalue']['prefix']='Jaar: '
    for i, jaar in enumerate([2017, 2018, 2019], start = 0):
        fig['layout']['sliders'][0]['steps'][i]['label']=jaar

    # Zet de margins
    fig.update_layout(margin={"r":0, "t": 50, "l": 20, "b": 100},
                      title = 'Totaal bekende CO₂-uitstoot per gemeente<br>(aardgas, elektr., stadswarmte woningen, voertuigbrandstoffen)',
                      title_x = 0.5,
                      title_y = 0.97,
                      font_family = "Calibri Light",
                      title_font_size = 18)

    st.plotly_chart(fig) # Laat de plot zien

