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
import plotly.express as px

st.set_page_config(page_title = 'Dashboard CO₂-uitstoot en woningdichtheid', page_icon = "🏘️", layout = 'wide')

st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 260px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 260px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

sidebar_page = st.sidebar.selectbox('Kies een pagina: ', ['CO₂-uitstoot', 'Woningdichtheid', 'Statistische analyse', 'Datasets en bronvermelding'])

if sidebar_page == 'CO₂-uitstoot':
    st.markdown("<h1 style='text-align: center; '>CO₂-uitstoot</h1>", unsafe_allow_html=True)
    
    radio_co2_type = st.radio('Type CO₂-uitstoot: ', ['Totale CO₂-uitstoot', 'Totale CO₂-uitstoot exclusief auto(snel)wegen', 'CO₂-uitstoot woningen'])
    
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
    
    geo_co2_merge = pd.read_csv('geo_co2_merge.csv')    
    histdata = geo_co2_merge[['Gemeenten', 'Jaar', 'totaal_co2', 'totaal_co2_ext_weg', 'co2_woningen']]
    
    if radio_co2_type == 'Totale CO₂-uitstoot':
        st.markdown("<h3 style='text-align: center; '>Totale CO₂-uitstoot op de kaart</h3>", unsafe_allow_html=True)
        st.info("Hier komt informatie")
        
        col1, col2 = st.columns([2,1])
        with col1:

            fig = go.Figure()

            c = 0

            for i, j, k in zip(dfs_year.year, dfs_year.geojson_year, dfs_year.geo_year):
                if c == 0:
                    v = True # In eerste instantie is alleen 2017 zichtbaar
                else:
                    v = False

                fig.add_trace(go.Choroplethmapbox(geojson=j, locations = k['Gemeenten'],
                                                  z = k['totaal_co2'],
                                                  colorscale='sunsetdark',
                                                  zmin=k['totaal_co2'].min(),
                                                  zmax=k['totaal_co2'].max(),
                                                  marker_opacity=0.8, marker_line_width=0.5, marker_line_color = 'indianred',
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
                              mapbox_zoom=5.5, mapbox_center = {"lat": 52.0893191, "lon": 5.1101691})

            # Edit slider labels
            fig['layout']['sliders'][0]['currentvalue']['prefix']='Jaar: '
            for i, jaar in enumerate([2017, 2018, 2019], start = 0):
                fig['layout']['sliders'][0]['steps'][i]['label']=jaar

            # Zet de margins
            fig.update_layout(margin={"r":0, "t": 50, "l": 20, "b": 100},
                              title = '<b>Totaal bekende CO₂-uitstoot (in ton) per gemeente<br>(aardgas, elektr., stadswarmte woningen, voertuigbrandstoffen)</b>',
                              title_x = 0.5,
                              title_y = 0.97,
                              font_family = "Calibri Light",
                              title_font_size = 18)

            st.plotly_chart(fig, use_container_width=True) # Laat de plot zien

        with col2:
            st.markdown('**Top 5: totale CO₂-uitstoot (in ton) per gemeente**')

            top5_2017_totaal = geo_co2_merge_2017.sort_values(by = 'totaal_co2', ascending = False)[['Gemeenten', 'totaal_co2']].reset_index(drop = True).head(5)
            top5_2018_totaal = geo_co2_merge_2018.sort_values(by = 'totaal_co2', ascending = False)[['Gemeenten', 'totaal_co2']].reset_index(drop = True).head(5)
            top5_2019_totaal = geo_co2_merge_2019.sort_values(by = 'totaal_co2', ascending = False)[['Gemeenten', 'totaal_co2']].reset_index(drop = True).head(5)

            top5_totaal = pd.DataFrame([top5_2017_totaal['Gemeenten'], top5_2017_totaal['totaal_co2'], top5_2018_totaal['totaal_co2'], top5_2019_totaal['totaal_co2']])
            top5_totaal = top5_totaal.transpose()
            top5_totaal.columns = ['Gemeenten', '2017', '2018', '2019']
            top5_totaal[["2017", "2018", "2019"]] = top5_totaal[["2017", "2018", "2019"]].astype(int)
            top5_totaal.index = top5_totaal['Gemeenten']
            top5_totaal = top5_totaal[['2017', '2018', '2019']]

            st.table(top5_totaal)
            
        st.markdown("<h3 style='text-align: center; '>Verdeling totale CO₂-uitstoot</h3>", unsafe_allow_html=True)
        st.info("Hier komt informatie")
        
        radio_zoom_hist = st.radio('Zoom: ', ['Volledig', 'Zonder uitschieters'])
        
        col1a, col1b = st.columns(2)
        with col1a:
            st.markdown('**Uitschieters totale CO₂-uitstoot (> 1,5 miljoen ton)**')
            
            outliers_totaal_2017 = (histdata[(histdata['totaal_co2'] >= 1500000) & 
                                 (histdata['Jaar'] == 2017)]
                        .sort_values(by = 'totaal_co2', ascending = False)['Gemeenten']
                        .reset_index(drop = True))
            outliers_totaal_2018 = (histdata[(histdata['totaal_co2'] >= 1500000) & 
                                 (histdata['Jaar'] == 2018)]
                        .sort_values(by = 'totaal_co2', ascending = False)['Gemeenten']
                        .reset_index(drop = True))
            outliers_totaal_2019 = (histdata[(histdata['totaal_co2'] >= 1500000) & 
                                 (histdata['Jaar'] == 2019)]
                        .sort_values(by = 'totaal_co2', ascending = False)['Gemeenten']
                        .reset_index(drop = True))
            
            outliers_totaal = pd.DataFrame({'2017': outliers_totaal_2017, '2018': outliers_totaal_2018, '2019': outliers_totaal_2019})
            outliers_totaal.index += 1
            outliers_totaal.fillna('-', inplace = True)

            st.table(outliers_totaal)

        with col1b:
            if radio_zoom_hist == 'Volledig':
                fig = px.histogram(histdata, x="totaal_co2", color = 'Jaar', nbins = 400,
                                   color_discrete_sequence=['#f29544', '#ae5f58', '#734656'])

                fig.update_layout(
                    title_text='<b>Verdeling totale CO₂-uitstoot (in ton) per gemeente</b>',
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "Calibri Light",
                    title_font_size = 22,
                    xaxis_title_font_size = 18,
                    yaxis_title_font_size = 18,
                    legend_title_font_size = 16,
                    plot_bgcolor='#d8dcdc'
                )

                st.plotly_chart(fig, use_container_width=True)                
                                
            elif radio_zoom_hist == 'Zonder uitschieters':
                fig = px.histogram(histdata, x="totaal_co2", color = 'Jaar', nbins = 400,
                                   color_discrete_sequence=['#f29544', '#ae5f58', '#734656'])

                fig.update_layout(
                    title_text='<b>Verdeling totale CO₂-uitstoot (in ton) per gemeente</b> (ingezoomd)',
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "Calibri Light",
                    title_font_size = 22,
                    xaxis_title_font_size = 18,
                    yaxis_title_font_size = 18,
                    legend_title_font_size = 16,
                    plot_bgcolor='#d8dcdc',
                    xaxis_range = [0, 1500000]
                )

                st.plotly_chart(fig, use_container_width=True)
            
    elif radio_co2_type == 'Totale CO₂-uitstoot exclusief auto(snel)wegen':
        st.markdown("<h3 style='text-align: center; '>Totale CO₂-uitstoot exclusief auto(snel)wegen op de kaart</h3>", unsafe_allow_html=True)
        st.info("Hier komt informatie")
        
        col3, col4 = st.columns([2,1])

        with col3:

            fig = go.Figure()

            c = 0

            for i, j, k in zip(dfs_year.year, dfs_year.geojson_year, dfs_year.geo_year):
                if c == 0:
                    v = True # In eerste instantie is alleen 2017 zichtbaar
                else:
                    v = False

                fig.add_trace(go.Choroplethmapbox(geojson=j, locations = k['Gemeenten'],
                                                  z = k['totaal_co2_ext_weg'],
                                                  colorscale='sunsetdark',
                                                  zmin=k['totaal_co2_ext_weg'].min(),
                                                  zmax=k['totaal_co2_ext_weg'].max(),
                                                  marker_opacity=0.8, marker_line_width=0.5, marker_line_color = 'indianred',
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
                              mapbox_zoom=5.5, mapbox_center = {"lat": 52.0893191, "lon": 5.1101691})

            # Edit slider labels
            fig['layout']['sliders'][0]['currentvalue']['prefix']='Jaar: '
            for i, jaar in enumerate([2017, 2018, 2019], start = 0):
                fig['layout']['sliders'][0]['steps'][i]['label']=jaar

            # Zet de margins
            fig.update_layout(margin={"r":0, "t": 50, "l": 20, "b": 100},
                              title = '<b>Totaal bekende CO₂-uitstoot (in ton) exclusief<br>CO₂-uitstoot auto(snel)wegen per gemeente</b>',
                              title_x = 0.5,
                              title_y = 0.97,
                              font_family = "Calibri Light",
                              title_font_size = 18)

            st.plotly_chart(fig, use_container_width=True) # Laat de plot zien

        with col4:
            st.markdown('**Top 5: totale CO₂-uitstoot (in ton) exclusief auto(snel)snelwegen per gemeente**')

            top5_2017_ext = geo_co2_merge_2017.sort_values(by = 'totaal_co2_ext_weg', ascending = False)[['Gemeenten', 'totaal_co2_ext_weg']].reset_index(drop = True).head(5)
            top5_2018_ext = geo_co2_merge_2018.sort_values(by = 'totaal_co2_ext_weg', ascending = False)[['Gemeenten', 'totaal_co2_ext_weg']].reset_index(drop = True).head(5)
            top5_2019_ext = geo_co2_merge_2019.sort_values(by = 'totaal_co2_ext_weg', ascending = False)[['Gemeenten', 'totaal_co2_ext_weg']].reset_index(drop = True).head(5)

            top5_ext = pd.DataFrame([top5_2017_ext['Gemeenten'], top5_2017_ext['totaal_co2_ext_weg'], top5_2018_ext['totaal_co2_ext_weg'], top5_2019_ext['totaal_co2_ext_weg']])
            top5_ext = top5_ext.transpose()
            top5_ext.columns = ['Gemeenten', '2017', '2018', '2019']
            top5_ext[["2017", "2018", "2019"]] = top5_ext[["2017", "2018", "2019"]].astype(int)
            top5_ext.index = top5_ext['Gemeenten']
            top5_ext = top5_ext[['2017', '2018', '2019']]

            st.table(top5_ext)
         
        st.markdown("<h3 style='text-align: center; '>Verdeling totale CO₂-uitstoot exclusief auto(snel)wegen</h3>", unsafe_allow_html=True)
        st.info("Hier komt informatie")
        
        radio_zoom_hist = st.radio('Zoom: ', ['Volledig', 'Zonder uitschieters'])
        
        col2a, col2b = st.columns(2)
        with col2a:
            st.markdown('**Uitschieters totale CO₂-uitstoot exclusief auto(snel)wegen (> 1 miljoen ton)**')
            
            outliers_ext_2017 = (histdata[(histdata['totaal_co2_ext_weg'] >= 1000000) & 
                                 (histdata['Jaar'] == 2017)]
                        .sort_values(by = 'totaal_co2_ext_weg', ascending = False)['Gemeenten']
                        .reset_index(drop = True))
            outliers_ext_2018 = (histdata[(histdata['totaal_co2_ext_weg'] >= 1000000) & 
                                 (histdata['Jaar'] == 2018)]
                        .sort_values(by = 'totaal_co2_ext_weg', ascending = False)['Gemeenten']
                        .reset_index(drop = True))
            outliers_ext_2019 = (histdata[(histdata['totaal_co2_ext_weg'] >= 1000000) & 
                                 (histdata['Jaar'] == 2019)]
                        .sort_values(by = 'totaal_co2_ext_weg', ascending = False)['Gemeenten']
                        .reset_index(drop = True))
            
            outliers_ext = pd.DataFrame({'2017': outliers_ext_2017, '2018': outliers_ext_2018, '2019': outliers_ext_2019})
            outliers_ext.index += 1
            outliers_ext.fillna('-', inplace = True)

            st.table(outliers_ext)

        with col2b:
            if radio_zoom_hist == 'Volledig':
                fig = px.histogram(histdata, x="totaal_co2_ext_weg", color = 'Jaar', nbins = 400,
                  color_discrete_sequence=['#f29544', '#ae5f58', '#734656'])

                fig.update_layout(
                    title_text='<b>Verdeling totale CO₂-uitstoot (in ton) exclusief auto(snel)wegen per gemeente</b>',
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "Calibri Light",
                    title_font_size = 22,
                    xaxis_title_font_size = 18,
                    yaxis_title_font_size = 18,
                    legend_title_font_size = 16,
                    plot_bgcolor='#d8dcdc'
                )

                st.plotly_chart(fig, use_container_width=True)                
                                
            elif radio_zoom_hist == 'Zonder uitschieters':
                fig = px.histogram(histdata, x="totaal_co2_ext_weg", color = 'Jaar', nbins = 400,
                  color_discrete_sequence=['#f29544', '#ae5f58', '#734656'])

                fig.update_layout(
                    title_text='<b>Verdeling totale CO₂-uitstoot (in ton) exclusief auto(snel)wegen per gemeente</b> (ingezoomd)',
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "Calibri Light",
                    title_font_size = 22,
                    xaxis_title_font_size = 18,
                    yaxis_title_font_size = 18,
                    legend_title_font_size = 16,
                    plot_bgcolor='#d8dcdc',
                    xaxis_range = [0, 1000000]
                )

                st.plotly_chart(fig, use_container_width=True)
    
    elif radio_co2_type == 'CO₂-uitstoot woningen':
        st.markdown("<h3 style='text-align: center; '>CO₂-uitstoot woningen</h1>", unsafe_allow_html=True)
        st.info("Hier komt informatie")
        
        col5, col6 = st.columns([2,1])

        with col5:

            fig = go.Figure()

            c = 0

            for i, j, k in zip(dfs_year.year, dfs_year.geojson_year, dfs_year.geo_year):
                if c == 0:
                    v = True # In eerste instantie is alleen 2017 zichtbaar
                else:
                    v = False

                fig.add_trace(go.Choroplethmapbox(geojson=j, locations = k['Gemeenten'],
                                                  z = k['co2_woningen'],
                                                  colorscale='sunsetdark',
                                                  zmin=k['co2_woningen'].min(),
                                                  zmax=k['co2_woningen'].max(),
                                                  marker_opacity=0.8, marker_line_width=0.5, marker_line_color = 'indianred',
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
                              mapbox_zoom=5.5, mapbox_center = {"lat": 52.0893191, "lon": 5.1101691})

            # Edit slider labels
            fig['layout']['sliders'][0]['currentvalue']['prefix']='Jaar: '
            for i, jaar in enumerate([2017, 2018, 2019], start = 0):
                fig['layout']['sliders'][0]['steps'][i]['label']=jaar

            # Zet de margins
            fig.update_layout(margin={"r":0, "t": 50, "l": 20, "b": 100},
                              title = '<b>CO₂-uitstoot (in ton) woningen per gemeente,<br>temperatuurgecorrigeerd (aardgas, elektriciteit en stadswarmte)</b>',
                              title_x = 0.5,
                              title_y = 0.97,
                              font_family = "Calibri Light",
                              title_font_size = 18)

            st.plotly_chart(fig, use_container_width=True) # Laat de plot zien

        with col6:
            st.markdown('**Top 5: CO₂-uitstoot (in ton) woningen per gemeente**')

            top5_2017_won = geo_co2_merge_2017.sort_values(by = 'co2_woningen', ascending = False)[['Gemeenten', 'co2_woningen']].reset_index(drop = True).head(5)
            top5_2018_won = geo_co2_merge_2018.sort_values(by = 'co2_woningen', ascending = False)[['Gemeenten', 'co2_woningen']].reset_index(drop = True).head(5)
            top5_2019_won = geo_co2_merge_2019.sort_values(by = 'co2_woningen', ascending = False)[['Gemeenten', 'co2_woningen']].reset_index(drop = True).head(5)

            top5_won = pd.DataFrame([top5_2017_won['Gemeenten'], top5_2017_won['co2_woningen'], top5_2018_won['co2_woningen'], top5_2019_won['co2_woningen']])
            top5_won = top5_won.transpose()
            top5_won.columns = ['Gemeenten', '2017', '2018', '2019']
            top5_won[["2017", "2018", "2019"]] = top5_won[["2017", "2018", "2019"]].astype(int)
            top5_won.index = top5_won['Gemeenten']
            top5_won = top5_won[['2017', '2018', '2019']]

            st.table(top5_won)
            
        st.markdown("<h3 style='text-align: center; '>Verdeling CO₂-uitstoot woningen</h3>", unsafe_allow_html=True)
        st.info("Hier komt informatie")
        
        radio_zoom_hist = st.radio('Zoom: ', ['Volledig', 'Zonder uitschieters'])
        
        col3a, col3b = st.columns(2)
        with col3a:
            st.markdown('**Uitschieters  CO₂-uitstoot woningen (> 300.000 ton)**')
            
            outliers_won_2017 = (histdata[(histdata['co2_woningen'] >= 300000) & 
                                 (histdata['Jaar'] == 2017)]
                        .sort_values(by = 'co2_woningen', ascending = False)['Gemeenten']
                        .reset_index(drop = True))
            outliers_won_2018 = (histdata[(histdata['co2_woningen'] >= 300000) & 
                                 (histdata['Jaar'] == 2018)]
                        .sort_values(by = 'co2_woningen', ascending = False)['Gemeenten']
                        .reset_index(drop = True))
            outliers_won_2019 = (histdata[(histdata['co2_woningen'] >= 300000) & 
                                 (histdata['Jaar'] == 2019)]
                        .sort_values(by = 'co2_woningen', ascending = False)['Gemeenten']
                        .reset_index(drop = True))
            
            outliers_won = pd.DataFrame({'2017': outliers_won_2017, '2018': outliers_won_2018, '2019': outliers_won_2019})
            outliers_won.index += 1
            outliers_won.fillna('-', inplace = True)

            st.table(outliers_ext)

        with col3b:
            if radio_zoom_hist == 'Volledig':
                fig = px.histogram(histdata, x="co2_woningen", color = 'Jaar', nbins = 400,
                  color_discrete_sequence=['#f29544', '#ae5f58', '#734656'])

                fig.update_layout(
                    title_text='<b>Verdeling CO₂-uitstoot (in ton) woningen per gemeente</b>',
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "Calibri Light",
                    title_font_size = 22,
                    xaxis_title_font_size = 18,
                    yaxis_title_font_size = 18,
                    legend_title_font_size = 16,
                    plot_bgcolor='#d8dcdc'
                )

                st.plotly_chart(fig, use_container_width=True)                
                                
            elif radio_zoom_hist == 'Zonder uitschieters':
                fig = px.histogram(histdata, x="co2_woningen", color = 'Jaar', nbins = 400,
                  color_discrete_sequence=['#f29544', '#ae5f58', '#734656'])

                fig.update_layout(
                    title_text='<b>Verdeling CO₂-uitstoot (in ton) woningen per gemeente</b> (ingezoomd)',
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "Calibri Light",
                    title_font_size = 22,
                    xaxis_title_font_size = 18,
                    yaxis_title_font_size = 18,
                    legend_title_font_size = 16,
                    plot_bgcolor='#d8dcdc',
                    xaxis_range = [0, 300000]
                )

                st.plotly_chart(fig, use_container_width=True)

