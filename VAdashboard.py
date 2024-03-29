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
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels as sm
import plotly.figure_factory as ff

####################################################################################################################################################################
####################################################################################################################################################################

st.set_page_config(page_title = 'Dashboard CO₂-uitstoot en woningdichtheid', page_icon = "🏘️", layout = 'wide')
url = "https://www.cbs.nl/nl-nl/achtergrond/2018/14/energieverbruik-van-particuliere-huishoudens"

st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        padding-top: 0.01rem;
    }}
</style>
""",
        unsafe_allow_html=True,
    )

def green_block(tekst):
     st.markdown(f'<div data-stale="false" class="element-container css-1e5imcs e1tzin5v1"><div class="stAlert"><div role="alert" data-baseweb="notification" class="st-ae st-af st-ag st-ah st-ai st-aj st-ak st-al st-am st-en st-ao st-ap st-aq st-ar st-as st-at st-au st-av st-aw st-ax st-ay st-az st-b9 st-b1 st-b2 st-b3 st-b4 st-b5 st-b6" style="background-color: rgb(210, 236, 190, 0.8); border-color: rgb(187, 217, 117); color: rgb(54, 77, 7)"><div class="st-b7"><div class="css-whx05o e13vu3m50"><div data-testid="stMarkdownContainer" class="css-1h7ljws e16nr0p30"><p>{tekst}</p></div></div></div></div></div></div>', unsafe_allow_html=True)
     
def green_block3(tekst, tekst2, tekst3):
     st.markdown(f'<div data-stale="false" class="element-container css-1e5imcs e1tzin5v1"><div class="stAlert"><div role="alert" data-baseweb="notification" class="st-ae st-af st-ag st-ah st-ai st-aj st-ak st-al st-am st-en st-ao st-ap st-aq st-ar st-as st-at st-au st-av st-aw st-ax st-ay st-az st-b9 st-b1 st-b2 st-b3 st-b4 st-b5 st-b6" style="background-color: rgb(210, 236, 190, 0.8); border-color: rgb(187, 217, 117); color: rgb(54, 77, 7)"><div class="st-b7"><div class="css-whx05o e13vu3m50"><div data-testid="stMarkdownContainer" class="css-1h7ljws e16nr0p30"><p>{tekst}</p><p>{tekst2}</p><p>{tekst3}</p></div></div></div></div></div></div>', unsafe_allow_html=True)
    
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 260px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 260px;
        margin-left: -260px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

sidebar_page = st.sidebar.selectbox('Kies een pagina: ', ['CO₂-uitstoot', 'Woningdichtheid', 'Statistische analyse', 'Datasets en bronvermelding'])

####################################################################################################################################################################
####################################################################################################################################################################

if sidebar_page == 'CO₂-uitstoot':
    st.markdown("<h1 style='text-align: center; '>CO₂-uitstoot</h1>", unsafe_allow_html=True)
    st.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
    st.sidebar.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
    
    # Inladen data co2
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
               
    # radiobutton   
    radio_co2_type = st.sidebar.radio('Type CO₂-uitstoot: ', ['Totale CO₂-uitstoot', 'Totale CO₂-uitstoot exclusief auto(snel)wegen', 'CO₂-uitstoot woningen'])
    
    ####################################################################################################################################################################
    
    if radio_co2_type == 'Totale CO₂-uitstoot':
        st.markdown("<h3 style='text-align: center; '>Totale CO₂-uitstoot op de kaart</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        col1, col2 = st.columns([2,1])
        with col1:

            fig = go.Figure()
            min_totaal = min(geo_co2_merge_2017['totaal_co2'].min(), geo_co2_merge_2018['totaal_co2'].min(), geo_co2_merge_2019['totaal_co2'].min())
            max_totaal = min(geo_co2_merge_2017['totaal_co2'].max(), geo_co2_merge_2018['totaal_co2'].max(), geo_co2_merge_2019['totaal_co2'].max())

            c = 0

            for i, j, k in zip(dfs_year.year, dfs_year.geojson_year, dfs_year.geo_year):
                if c == 0:
                    v = True # In eerste instantie is alleen 2017 zichtbaar
                else:
                    v = False

                fig.add_trace(go.Choroplethmapbox(geojson=j, locations = k['Gemeenten'],
                                                  z = k['totaal_co2'],
                                                  colorscale='sunsetdark',
                                                  zmin=min_totaal,
                                                  zmax=max_totaal,
                                                  marker_opacity=0.8, marker_line_width=0.5, marker_line_color = 'indianred',
                                                  name = i, visible = v,
                                                  featureidkey="properties.statnaam",
                                                  colorbar={"title": 'CO₂-uitstoot (in ton)'},
                                                  hoverlabel = {'bgcolor': '#d2ecbe'}))
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
                              title = '<b>Totale CO₂-uitstoot (in ton) per gemeente</b>',
                              title_x = 0.2,
                              title_y = 0.97,
                              font_family = "sans-serif",
                              title_font_size = 16)

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
            
            green_block('''Met <strong>totale CO₂-uitstoot</strong> wordt de totaal bekende CO₂-uitstoot bedoeld. Dit betreft CO₂-uitstoot wegens aardgas, elektriciteit, stadwarmte woningen en voertuigbrandstoffen.''')
        
        st.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; '>Verdeling totale CO₂-uitstoot</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        med_co2_totaal = histdata.groupby('Jaar')['totaal_co2'].median()
        
        col1a, col1b = st.columns(2)
        with col1a:
            radio_zoom_hist = st.radio('Zoom: ', ['Volledig', 'Zonder uitschieters'])
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
                                   color_discrete_sequence=['rgb(131, 30, 113)', 'rgb(237, 106, 111)', 'rgb(250, 200, 116)'])
                
                fig.update_layout(barmode='group')

                fig.update_layout(
                    title_text='<b>Verdeling totale CO₂-uitstoot (in ton) per gemeente</b>',
                    title_x = 0.5,
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "sans-serif",
                    title_font_size = 16,
                    xaxis_title_font_size = 14,
                    yaxis_title_font_size = 14,
                    legend_title_font_size = 14,
                    plot_bgcolor='#d8dcdc'
                )
                fig.add_annotation(xref = 'paper', yref = 'paper', x = 0.9, y = 0.92,
                                   text = "mediaan 2017: "+ str(med_co2_totaal.get(2017)) + '<br>' +
                                   "mediaan 2018: " + str(med_co2_totaal.get(2018)) + '<br>' +
                                   "mediaan 2019: " + str(med_co2_totaal.get(2019)),
                                   showarrow = False)

                st.plotly_chart(fig, use_container_width=True)                
                                
            elif radio_zoom_hist == 'Zonder uitschieters':
                fig = px.histogram(histdata, x="totaal_co2", color = 'Jaar', nbins = 400,
                                   color_discrete_sequence=['rgb(131, 30, 113)', 'rgb(237, 106, 111)', 'rgb(250, 200, 116)'])
                
                fig.update_layout(barmode='group')

                fig.update_layout(
                    title_text='<b>Verdeling totale CO₂-uitstoot (in ton) per gemeente</b> (ingezoomd)',
                    title_x = 0.5,
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "sans-serif",
                    title_font_size = 16,
                    xaxis_title_font_size = 14,
                    yaxis_title_font_size = 14,
                    legend_title_font_size = 14,
                    plot_bgcolor='#d8dcdc',
                    xaxis_range = [0, 1500000]
                )
                
                fig.add_annotation(xref = 'paper', yref = 'paper', x = 0.9, y = 0.92,
                                   text = "mediaan 2017: "+ str(med_co2_totaal.get(2017)) + '<br>' +
                                   "mediaan 2018: " + str(med_co2_totaal.get(2018)) + '<br>' +
                                   "mediaan 2019: " + str(med_co2_totaal.get(2019)),
                                   showarrow = False)

                st.plotly_chart(fig, use_container_width=True)

    ####################################################################################################################################################################                

    elif radio_co2_type == 'Totale CO₂-uitstoot exclusief auto(snel)wegen':
        st.markdown("<h3 style='text-align: center; '>Totale CO₂-uitstoot exclusief auto(snel)wegen op de kaart</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        col3, col4 = st.columns([2,1])

        with col3:

            fig = go.Figure()
            min_ext = min(geo_co2_merge_2017['totaal_co2_ext_weg'].min(), geo_co2_merge_2018['totaal_co2_ext_weg'].min(), geo_co2_merge_2019['totaal_co2_ext_weg'].min())
            max_ext = min(geo_co2_merge_2017['totaal_co2_ext_weg'].max(), geo_co2_merge_2018['totaal_co2_ext_weg'].max(), geo_co2_merge_2019['totaal_co2_ext_weg'].max())
               
            c = 0

            for i, j, k in zip(dfs_year.year, dfs_year.geojson_year, dfs_year.geo_year):
                if c == 0:
                    v = True # In eerste instantie is alleen 2017 zichtbaar
                else:
                    v = False

                fig.add_trace(go.Choroplethmapbox(geojson=j, locations = k['Gemeenten'],
                                                  z = k['totaal_co2_ext_weg'],
                                                  colorscale='sunsetdark',
                                                  zmin=min_ext,
                                                  zmax=max_ext,
                                                  marker_opacity=0.8, marker_line_width=0.5, marker_line_color = 'indianred',
                                                  name = i, visible = v,
                                                  featureidkey="properties.statnaam",
                                                  colorbar={"title": 'CO₂-uitstoot (in ton)'},
                                                  hoverlabel = {'bgcolor': '#d2ecbe'}))
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
                              title_x = 0.2,
                              title_y = 0.97,
                              font_family = "sans-serif",
                              title_font_size = 16)

            st.plotly_chart(fig, use_container_width=True) # Laat de plot zien

        with col4:
            st.markdown('**Top 5: totale CO₂-uitstoot (in ton) exclusief auto(snel)wegen per gemeente**')

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
            green_block("Met <strong>totale CO₂-uitstoot exclusief auto(snel)wegen</strong> wordt de totaal bekende CO₂-uitstoot bedoeld exclusief CO₂-uitstoot wegens voertuigbrandstoffen op auto(snel)wegen.")
            
        st.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; '>Verdeling totale CO₂-uitstoot exclusief auto(snel)wegen</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        med_co2_ext = histdata.groupby('Jaar')['totaal_co2_ext_weg'].median()
        
        col2a, col2b = st.columns(2)
        with col2a:
            radio_zoom_hist = st.radio('Zoom: ', ['Volledig', 'Zonder uitschieters'])
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
                                   color_discrete_sequence=['rgb(131, 30, 113)', 'rgb(237, 106, 111)', 'rgb(250, 200, 116)'])
                
                fig.update_layout(barmode='group')

                fig.update_layout(
                    title_text='<b>Verdeling totale CO₂-uitstoot (in ton) exclusief<br>auto(snel)wegen per gemeente</b>',
                    title_x = 0.5,
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "sans-serif",
                    title_font_size = 16,
                    xaxis_title_font_size = 14,
                    yaxis_title_font_size = 14,
                    legend_title_font_size = 14,
                    plot_bgcolor='#d8dcdc'
                )
                
                fig.add_annotation(xref = 'paper', yref = 'paper', x = 0.9, y = 0.87,
                                   text = "mediaan 2017: "+ str(med_co2_ext.get(2017)) + '<br>' +
                                   "mediaan 2018: " + str(med_co2_ext.get(2018)) + '<br>' +
                                   "mediaan 2019: " + str(med_co2_ext.get(2019)),
                                   showarrow = False)

                st.plotly_chart(fig, use_container_width=True)                
                                
            elif radio_zoom_hist == 'Zonder uitschieters':
                fig = px.histogram(histdata, x="totaal_co2_ext_weg", color = 'Jaar', nbins = 400,
                                   color_discrete_sequence=['rgb(131, 30, 113)', 'rgb(237, 106, 111)', 'rgb(250, 200, 116)'])
                
                fig.update_layout(barmode='group')

                fig.update_layout(
                    title_text='<b>Verdeling totale CO₂-uitstoot (in ton) exclusief<br>auto(snel)wegen per gemeente</b> (ingezoomd)',
                    title_x = 0.5,
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "sans-serif",
                    title_font_size = 16,
                    xaxis_title_font_size = 14,
                    yaxis_title_font_size = 14,
                    legend_title_font_size = 14,
                    plot_bgcolor='#d8dcdc',
                    xaxis_range = [0, 1000000]
                )
                
                fig.add_annotation(xref = 'paper', yref = 'paper', x = 0.9, y = 0.87,
                                   text = "mediaan 2017: "+ str(med_co2_ext.get(2017)) + '<br>' +
                                   "mediaan 2018: " + str(med_co2_ext.get(2018)) + '<br>' +
                                   "mediaan 2019: " + str(med_co2_ext.get(2019)),
                                   showarrow = False)

                st.plotly_chart(fig, use_container_width=True)
    
    ####################################################################################################################################################################

    elif radio_co2_type == 'CO₂-uitstoot woningen':
        st.markdown("<h3 style='text-align: center; '>CO₂-uitstoot woningen</h1>", unsafe_allow_html=True)
        st.markdown("")
        st.sidebar.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
        st.sidebar.markdown("*De waardes zijn **temperatuurgecorrigeerd**, om het klimaateffect uit de cijfers te halen. Meer hierover lees je [hier](%s)." % url)
        
        col5, col6 = st.columns([2,1])

        with col5:

            fig = go.Figure()
            min_won = min(geo_co2_merge_2017['co2_woningen'].min(), geo_co2_merge_2018['co2_woningen'].min(), geo_co2_merge_2019['co2_woningen'].min())
            max_won = min(geo_co2_merge_2017['co2_woningen'].max(), geo_co2_merge_2018['co2_woningen'].max(), geo_co2_merge_2019['co2_woningen'].max())

            c = 0

            for i, j, k in zip(dfs_year.year, dfs_year.geojson_year, dfs_year.geo_year):
                if c == 0:
                    v = True # In eerste instantie is alleen 2017 zichtbaar
                else:
                    v = False

                fig.add_trace(go.Choroplethmapbox(geojson=j, locations = k['Gemeenten'],
                                                  z = k['co2_woningen'],
                                                  colorscale='sunsetdark',
                                                  zmin=min_won,
                                                  zmax=max_won,
                                                  marker_opacity=0.8, marker_line_width=0.5, marker_line_color = 'indianred',
                                                  name = i, visible = v,
                                                  featureidkey="properties.statnaam",
                                                  colorbar={"title": 'CO₂-uitstoot (in ton)'},
                                                  hoverlabel = {'bgcolor': '#d2ecbe'}))
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
                              title = '<b>CO₂-uitstoot (in ton) woningen per gemeente, temperatuurgecorrigeerd*</b>',
                              title_x = 0.05,
                              title_y = 0.97,
                              font_family = "sans-serif",
                              title_font_size = 16)

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
            green_block("Met <strong>CO₂-uitstoot woningen</strong> wordt de CO₂-uitstoot van woningen wegens aardgas, elektriciteit en stadswarmte bedoeld.")
        
        st.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
            
        st.markdown("<h3 style='text-align: center; '>Verdeling CO₂-uitstoot woningen</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        med_co2_won = histdata.groupby('Jaar')['co2_woningen'].median()
        
        col3a, col3b = st.columns(2)
        with col3a:
            radio_zoom_hist = st.radio('Zoom: ', ['Volledig', 'Zonder uitschieters'])
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

            st.table(outliers_won)

        with col3b:
            if radio_zoom_hist == 'Volledig':
                fig = px.histogram(histdata, x="co2_woningen", color = 'Jaar', nbins = 400,
                                   color_discrete_sequence=['rgb(131, 30, 113)', 'rgb(237, 106, 111)', 'rgb(250, 200, 116)'])
                
                fig.update_layout(barmode='group')

                fig.update_layout(
                    title_text='<b>Verdeling CO₂-uitstoot (in ton) woningen per gemeente</b>',
                    title_x = 0.5,
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "sans-serif",
                    title_font_size = 16,
                    xaxis_title_font_size = 14,
                    yaxis_title_font_size = 14,
                    legend_title_font_size = 14,
                    plot_bgcolor='#d8dcdc'
                )
                
                fig.add_annotation(xref = 'paper', yref = 'paper', x = 0.9, y = 0.945,
                                   text = "mediaan 2017: "+ str(med_co2_won.get(2017)) + '<br>' +
                                   "mediaan 2018: " + str(med_co2_won.get(2018)) + '<br>' +
                                   "mediaan 2019: " + str(med_co2_won.get(2019)),
                                   showarrow = False)

                st.plotly_chart(fig, use_container_width=True)                
                                
            elif radio_zoom_hist == 'Zonder uitschieters':
                fig = px.histogram(histdata, x="co2_woningen", color = 'Jaar', nbins = 400,
                                   color_discrete_sequence=['rgb(131, 30, 113)', 'rgb(237, 106, 111)', 'rgb(250, 200, 116)'])
                
                fig.update_layout(barmode='group')

                fig.update_layout(
                    title_text='<b>Verdeling CO₂-uitstoot (in ton) woningen per gemeente</b> (ingezoomd)',
                    title_x = 0.5,
                    xaxis_title_text='CO₂-uitstoot (in ton)',
                    yaxis_title_text='Frequentie (aantal gemeenten)',
                    font_family = "sans-serif",
                    title_font_size = 16,
                    xaxis_title_font_size = 14,
                    yaxis_title_font_size = 14,
                    legend_title_font_size = 14,
                    plot_bgcolor='#d8dcdc',
                    xaxis_range = [0, 300000]
                )
                
                fig.add_annotation(xref = 'paper', yref = 'paper', x = 0.9, y = 0.945,
                                   text = "mediaan 2017: "+ str(med_co2_won.get(2017)) + '<br>' +
                                   "mediaan 2018: " + str(med_co2_won.get(2018)) + '<br>' +
                                   "mediaan 2019: " + str(med_co2_won.get(2019)),
                                   showarrow = False)

                st.plotly_chart(fig, use_container_width=True)
                    
####################################################################################################################################################################     
####################################################################################################################################################################

if sidebar_page == 'Woningdichtheid':
     st.markdown("<h1 style='text-align: center; '>Woningdichtheid</h1>", unsafe_allow_html=True)
     st.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
     st.markdown("<h3 style='text-align: center; '>Woningdichtheid per gemeente op de kaart</h3>", unsafe_allow_html=True)
     st.markdown("")
    
     # Inladen data woningdichtheid
     woningdichtheid = pd.read_csv('woningdichtheid.csv')
     geo_woningdichtheid_2019_merge = pd.read_csv('geo_woningdichtheid_2019_merge.csv')
    
     with open('geo_woningdichtheid_2019_merge.json', encoding = "ISO-8859-1") as geofile:
          geo_woningdichtheid_2019_merge_json = json.load(geofile) 
          
     ####################################################################################################################################################################
    
     col1, col2 = st.columns([2,1])
    
     with col1:
          # Kaart woningdichtheid
          fig_wd = go.Figure(go.Choroplethmapbox(geojson=geo_woningdichtheid_2019_merge_json,
                                          locations=geo_woningdichtheid_2019_merge['Gemeenten'],
                                          z=geo_woningdichtheid_2019_merge['Woningdichtheid'],
                                          colorscale="deep",
                                          zmin=geo_woningdichtheid_2019_merge['Woningdichtheid'].min(),
                                          zmax=geo_woningdichtheid_2019_merge['Woningdichtheid'].max(),
                                          marker_opacity=0.8, marker_line_width=0.5, marker_line_color = 'cadetblue',
                                          featureidkey="properties.statnaam",
                                          colorbar={'title':'<b>Woningdichtheid<br>(aantal woningen<br>per km²)</b>'},
                                          hoverlabel = {'bgcolor': '#ac247c'}
                                         ))

          fig_wd.update_layout(mapbox_style="carto-positron",
                            mapbox_zoom=5.5, mapbox_center = {"lat": 52.0893191, "lon": 5.1101691})

          fig_wd.update_layout(margin={"r":0,"t":50,"l":100,"b":100},
                            title = '<b>Woningdichtheid (aantal woningen per km²) per gemeente in 2019</b>',
                            title_x = 0.5,
                            title_y = 0.97,
                            font_family = "sans-serif",
                            title_font_size = 16)

          # Buttons maken
          buttons = [{'label': 'Alle',
                      'method': 'relayout', 
                      'args': [{'mapbox.center.lat': 52.0893191,
                                'mapbox.center.lon': 5.1101691,
                                'mapbox.zoom': 5.5}]},
                     {'label': 'Den Haag, Leiden en Delft', 
                      'method': 'relayout', 
                      'args': [{'mapbox.center.lat': 52.080476,
                                'mapbox.center.lon': 4.373835,
                                'mapbox.zoom': 9.0}]},
                     {'label': 'Amsterdam en Haarlem', 
                      'method': 'relayout', 
                      'args': [{'mapbox.center.lat': 52.361216,
                                'mapbox.center.lon': 4.825168,
                                'mapbox.zoom': 9.3}]}]

          # Buttons toevoegen
          fig_wd.update_layout(updatemenus=[{'type': 'buttons', 'buttons': buttons, 'x': -0.02, 'y': 0.92, 'direction' : 'down'}])
  
          # Tekst voor button en legenda toevoegen
          fig_wd.update_layout(annotations=[dict(text="Zoomlevel (top 5 gemeenten)", font_size=13, x=-0.41, y=1, xref="paper", yref="paper",
                                              align="left", showarrow=False)])

          st.plotly_chart(fig_wd, use_container_width=True)
        
     with col2:
          st.markdown('**Top 5: Woningdichtheid (aantal woningen per km²) per gemeente in 2019**')
          top5_woningdichtheid_2019 = geo_woningdichtheid_2019_merge.sort_values(by = 'Woningdichtheid', ascending = False)[['Gemeenten', 'Woningdichtheid']].reset_index(drop = True).head(5)
          top5_woningdichtheid_2019['Woningdichtheid'] = top5_woningdichtheid_2019['Woningdichtheid'].astype(int)
          top5_woningdichtheid_2019.index = top5_woningdichtheid_2019['Gemeenten']
          top5_woningdichtheid_2019 = pd.DataFrame(top5_woningdichtheid_2019['Woningdichtheid'])
          st.table(top5_woningdichtheid_2019)
    
     ####################################################################################################################################################################
     st.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
     st.markdown("<h3 style='text-align: center; '>Verdeling woningdichtheid</h3>", unsafe_allow_html=True)
     st.markdown("")
     
     col1, col2 = st.columns([1,4])
     with col1:
          radio_boxplot = st.radio('Weergave', ['Met puntenwolk', 'Zonder puntenwolk', 'Zonder uitschieters'])
     
     with col2:
          if radio_boxplot == 'Met puntenwolk':
 
               boxplot_wd = go.Figure()
 
               boxplot_wd.add_trace(go.Box(y=woningdichtheid[woningdichtheid['Jaar'] == 2017]['Woningdichtheid'],
                                           name='2017',
                                           text='<b>' + woningdichtheid[woningdichtheid['Jaar'] == 2017]['Gemeenten'] + '</b>',
                                           fillcolor='rgb(210,236,190)',
                                           marker_color='rgb(124,177,88)',
                                           marker_size=4,
                                           whiskerwidth=0.3,
                                           boxpoints='all',
                                           jitter=0.7,
                                           pointpos=2
                                           ))

               boxplot_wd.add_trace(go.Box(y=woningdichtheid[woningdichtheid['Jaar'] == 2018]['Woningdichtheid'],
                                           name='2018',
                                           text='<b>' + woningdichtheid[woningdichtheid['Jaar'] == 2018]['Gemeenten'] + '</b>',
                                           fillcolor='rgb(171,218,205)',
                                           marker_color='rgb(70,135,156)',
                                           marker_size=4,
                                           whiskerwidth=0.3,
                                           boxpoints='all',
                                           jitter=0.7,
                                           pointpos=2
                                           ))

               boxplot_wd.add_trace(go.Box(y=woningdichtheid[woningdichtheid['Jaar'] == 2019]['Woningdichtheid'],
                                           name='2019',
                                           text= '<b>' + woningdichtheid[woningdichtheid['Jaar'] == 2019]['Gemeenten'] + '</b>',
                                           fillcolor='rgb(196,192,211)',
                                           marker_color='rgb(59,51,95)',
                                           marker_size=4,
                                           whiskerwidth=0.3,
                                           boxpoints='all',
                                           jitter=0.7,
                                           pointpos=2
                                           ))
 
               boxplot_wd.update_traces(width=0.4)
 
               boxplot_wd.update_layout(title_text="<b>Woningdichtheid (aantal woningen per km²) per gemeente per jaar</b>",
                                        plot_bgcolor='whitesmoke',
                                        yaxis_title="Woningdichtheid<br>(aantal woningen per km²)",
                                        xaxis_title="Jaar",
                                        legend_title_text='Jaar',
                                        font_family = "sans-serif",
                                        yaxis_title_font_size = 14,
                                        xaxis_title_font_size = 14,
                                        legend_title_font_size = 14,
                                        title_font_size = 16,
                                        width=900,
                                        height=600
                                       )

               med_won_jaar = woningdichtheid.groupby('Jaar')['Woningdichtheid'].median()

               for i in [2017, 2018, 2019]:
                 boxplot_wd.add_annotation(x = i-2017, y = med_won_jaar.get(i) + 60,
                                           text = "mediaan: "+str(med_won_jaar.get(i)),
                                           showarrow = False)          
 
               st.plotly_chart(boxplot_wd)
 
          elif radio_boxplot == "Zonder puntenwolk":
               boxplot_wd = go.Figure()
 
               boxplot_wd.add_trace(go.Box(y=woningdichtheid[woningdichtheid['Jaar'] == 2017]['Woningdichtheid'],
                                           name='2017',
                                           text='<b>' + woningdichtheid[woningdichtheid['Jaar'] == 2017]['Gemeenten'] + '</b>',
                                           fillcolor='rgb(210,236,190)',
                                           marker_color='rgb(124,177,88)',
                                           marker_size=4,
                                           whiskerwidth=0.3,
                                           ))
 
               boxplot_wd.add_trace(go.Box(y=woningdichtheid[woningdichtheid['Jaar'] == 2018]['Woningdichtheid'],
                                           name='2018',
                                           text= '<b>' + woningdichtheid[woningdichtheid['Jaar'] == 2018]['Gemeenten'] + '</b>',
                                           fillcolor='rgb(171,218,205)',
                                           marker_color='rgb(70,135,156)',
                                           marker_size=4,
                                           whiskerwidth=0.3,
                                           ))
 
               boxplot_wd.add_trace(go.Box(y=woningdichtheid[woningdichtheid['Jaar'] == 2019]['Woningdichtheid'],
                                           name='2019',
                                           text='<b>' + woningdichtheid[woningdichtheid['Jaar'] == 2019]['Gemeenten'] + '</b>',
                                           fillcolor='rgb(196,192,211)',
                                           marker_color='rgb(59,51,95)',
                                           marker_size=4,
                                           whiskerwidth=0.3,
                                           ))
 
               boxplot_wd.update_traces(width=0.4)
 
               boxplot_wd.update_layout(title_text="<b>Woningdichtheid (aantal woningen per km²) per gemeente per jaar</b>",
                                        plot_bgcolor='whitesmoke',
                                        yaxis_title="Woningdichtheid<br>(aantal woningen per km²)",
                                        xaxis_title="Jaar",
                                        legend_title_text='Jaar',
                                        font_family = "sans-serif",
                                        yaxis_title_font_size = 14,
                                        xaxis_title_font_size = 14,
                                        legend_title_font_size = 14,
                                        title_font_size = 16,
                                        width=900,
                                        height=600
                                       )
 
               med_won_jaar = woningdichtheid.groupby('Jaar')['Woningdichtheid'].median()
 
               for i in [2017, 2018, 2019]:
                 boxplot_wd.add_annotation(x = i-2017, y = med_won_jaar.get(i) + 60,
                                           text = "mediaan: "+str(med_won_jaar.get(i)),
                                           showarrow = False) 
 
               st.plotly_chart(boxplot_wd)
 
          elif radio_boxplot == 'Zonder uitschieters':
               boxplot_wd = go.Figure()
 
               boxplot_wd.add_trace(go.Box(y=woningdichtheid[woningdichtheid['Jaar'] == 2017]['Woningdichtheid'],
                                           name='2017',
                                           text='<b>' +woningdichtheid[woningdichtheid['Jaar'] == 2017]['Gemeenten']+'</b>',
                                           fillcolor='rgb(210,236,190)',
                                           marker_color='rgb(124,177,88)',
                                           marker_size=4,
                                           marker={'opacity':0},
                                           whiskerwidth=0.3
                                           ))
 
               boxplot_wd.add_trace(go.Box(y=woningdichtheid[woningdichtheid['Jaar'] == 2018]['Woningdichtheid'],
                                           name='2018',
                                           text='<b>'+woningdichtheid[woningdichtheid['Jaar'] == 2018]['Gemeenten']+'</b>',
                                           fillcolor='rgb(171,218,205)',
                                           marker_color='rgb(70,135,156)',
                                           marker_size=4,
                                           marker={'opacity':0},
                                           whiskerwidth=0.3
                                           ))
 
               boxplot_wd.add_trace(go.Box(y=woningdichtheid[woningdichtheid['Jaar'] == 2019]['Woningdichtheid'],
                                           name='2019',
                                           text='<b>'+woningdichtheid[woningdichtheid['Jaar'] == 2019]['Gemeenten']+'</b>',
                                           fillcolor='rgb(196,192,211)',
                                           marker_color='rgb(59,51,95)',
                                           marker_size=4,
                                           marker={'opacity':0},
                                           whiskerwidth=0.3
                                           ))
 
               boxplot_wd.update_traces(width=0.4)
 
               boxplot_wd.update_layout(title_text="<b>Woningdichtheid (aantal woningen per km²) per gemeente per jaar</b>",
                                        plot_bgcolor='whitesmoke',
                                        yaxis_title="Woningdichtheid<br>(aantal woningen per km²)",
                                        xaxis_title="Jaar",
                                        legend_title_text='Jaar',
                                        font_family = "sans-serif",
                                        yaxis_title_font_size = 14,
                                        xaxis_title_font_size = 14,
                                        legend_title_font_size = 14,
                                        title_font_size = 16,
                                        width=900,
                                        height=600,
                                        yaxis_range = [-100, 1200]
                                       )
 
               med_won_jaar = woningdichtheid.groupby('Jaar')['Woningdichtheid'].median()
 
               for i in [2017, 2018, 2019]:
                 boxplot_wd.add_annotation(x = i-2017, y = med_won_jaar.get(i) + 40,
                                           text = "mediaan: "+str(med_won_jaar.get(i)),
                                           showarrow = False) 
 
               st.plotly_chart(boxplot_wd)
 
####################################################################################################################################################################
####################################################################################################################################################################          
          
if sidebar_page == 'Statistische analyse':
    st.markdown("<h1 style='text-align: center; '>Statistische analyse: CO₂-uitstoot en woningdichtheid</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
    
    # Inladen data merged
    co2_woningdichtheid_2019_merge = pd.read_csv('co2_woningdichtheid_2019_merge.csv')
     
    radio_analyse = st.sidebar.radio('Analyse: ', ['Correlatie', 'Regressie'])
    if radio_analyse == 'Correlatie':

        st.markdown("<h3 style='text-align: center; '>Correlatie</h3>", unsafe_allow_html=True)
        st.markdown("")

        col1, col2 = st.columns([1.3, 1])
        with col1:
            # Scattermatrix
            scatter_co2_wd = go.Figure(data=go.Splom(dimensions=[dict(label='totaal CO₂', values=co2_woningdichtheid_2019_merge['totaal_co2']),
                                                                 dict(label='totaal CO₂ excl. weg', values=co2_woningdichtheid_2019_merge['totaal_co2_ext_weg']),
                                                                 dict(label='CO₂ woningen', values=co2_woningdichtheid_2019_merge['co2_woningen']),
                                                                 dict(label='woningdichtheid', values=co2_woningdichtheid_2019_merge['Woningdichtheid'])],
                                                     diagonal_visible=False,
                                                     text=co2_woningdichtheid_2019_merge['Gemeenten'],
                                                     marker=dict(color='rgb(172, 36, 124)',
                                                                 line=dict(width=0.5, color='white')
                                                                 )
                                                     ))

            scatter_co2_wd.update_layout({"xaxis4":{"tickfont":{"size":11}}},
                                         title='<b>CO₂-uitstoot en woningdichtheid per gemeente in 2019</b>',
                                         height=700,
                                         font_family = "sans-serif",
                                         title_font_size = 16,
                                         plot_bgcolor='whitesmoke')

            st.plotly_chart(scatter_co2_wd, use_container_width=True)

        with col2:
        # Correlatiematrix
            cor = co2_woningdichtheid_2019_merge[['totaal_co2', 'totaal_co2_ext_weg', 'co2_woningen', 'Woningdichtheid']].corr()
            cor2 = cor.values.tolist()
            cor2_text = [[str(round(y, 3)) for y in x] for x in cor2]

            hm = ff.create_annotated_heatmap(cor2,
                                              x = ['totaal CO₂', 'totaal CO₂ excl. weg', 'CO₂ woningen', 'woningdichtheid'],
                                              y = ['totaal CO₂', 'totaal CO₂ excl. weg', 'CO₂ woningen', 'woningdichtheid'],
                                              annotation_text = cor2_text,
                                              showscale=True,
                                              colorscale = 'sunsetdark')

            hm['layout']['yaxis']['autorange'] = "reversed"
            hm['layout']['xaxis'].update(side='bottom')
            hm.update_layout(title_text = '<b>Correlatie heatmap</b>',
                              title_font_size = 16,
                              yaxis_tickfont_size = 14,
                              xaxis_tickfont_size = 14,
                              font_family = 'sans-serif',
                              title_x = 0.5)

            st.plotly_chart(hm, use_container_width=True)
        
            df = pd.DataFrame({'Variabele': ['CO₂-uitstoot', 'Woningdichtheid'], 'Eenheid': ['Ton', 'Aantal woningen per km²']})
            df.index = ["", ""]
            st.table(df)
    
    if radio_analyse == 'Regressie':
        st.markdown("<h3 style='text-align: center; '>Regressie</h3>", unsafe_allow_html=True)
        green_block('''In de correlatie heatmap werd duidelijk dat <strong>woningdichtheid</strong> het meest correleert met (zoals te verwachten) <strong>CO₂ woningen</strong>. Om te onderzoeken hoe goed de woningdichtheid voorspeld kan worden op basis van de CO₂-uitstoot van woningen, is er een regressie uitgevoerd. De resultaten hiervan zijn op deze pagina te bekijken.''')
        st.markdown("")
        
        st.sidebar.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
        checkbox_trend = st.sidebar.checkbox('Laat trendlijn zien')
        
        with st.expander("Bekijk model samenvatting"):
            col1, col2, col3 = st.columns([0.35,2,0.35])
            with col1:
                st.markdown("")
            with col2:
                X = sm.add_constant(co2_woningdichtheid_2019_merge['Woningdichtheid'])
                Y = co2_woningdichtheid_2019_merge['co2_woningen']
                model = sm.OLS(Y, X).fit()
                st.code(model.summary())
            with col3:
                st.markdown("")
                
     
        if checkbox_trend:

            scatter_co2_wd2a = px.scatter(co2_woningdichtheid_2019_merge,
                                         x='Woningdichtheid',
                                         y='co2_woningen',
                                         hover_data=['Gemeenten'],
                                         trendline="ols",
                                         color_discrete_sequence=['rgb(172, 36, 124)'],
                                         trendline_color_override='rgb(125,29,111)')

            scatter_co2_wd2a.update_layout(title='<b>CO₂-uitstoot (in ton) woningen en woningdichtheid (aantal woningen per km²) per gemeente in 2019</b>',
                                           title_x = 0.5,
                                          xaxis_title='Woningdichtheid (aantal woningen per km²)',
                                          yaxis_title='CO₂-uitstoot woningen (in ton)',
                                          yaxis_title_font_size = 14,
                                          xaxis_title_font_size = 14,
                                          width=800, height=600,
                                          font_family = "sans-serif",
                                          title_font_size = 16,
                                          plot_bgcolor='whitesmoke')

            st.plotly_chart(scatter_co2_wd2a, use_container_width=True)

        else:
            scatter_co2_wd2b = px.scatter(co2_woningdichtheid_2019_merge,
                                         x='Woningdichtheid',
                                         y='co2_woningen',
                                         hover_data=['Gemeenten'],
                                         color_discrete_sequence=['rgb(172, 36, 124)'])

            scatter_co2_wd2b.update_layout(title='<b>CO₂-uitstoot (in ton) woningen en woningdichtheid (aantal woningen per km²) per gemeente in 2019</b>',
                                           title_x = 0.5,
                                          xaxis_title='Woningdichtheid (aantal woningen per km²)',
                                          yaxis_title='CO₂-uitstoot woningen (in ton)',
                                          yaxis_title_font_size = 14,
                                          xaxis_title_font_size = 14,
                                          width=800, height=600,
                                          font_family = "sans-serif",
                                          title_font_size = 16,
                                          plot_bgcolor='whitesmoke')

            st.plotly_chart(scatter_co2_wd2b, use_container_width=True)
        
####################################################################################################################################################################
####################################################################################################################################################################

if sidebar_page == 'Datasets en bronvermelding':
    st.markdown("<h1 style='text-align: center; '>Datasets en bronvermelding</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
    st.sidebar.markdown("*De tabellen op deze pagina tonen de eerste vijf rijen van de datasets die gebruikt zijn in dit dashboard. Dit zijn niet de ruwe data, maar de geïnspecteerde en opgeschoonde data.")
    st.sidebar.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
    st.sidebar.markdown("Makers: Lisa Mulder (500831854) en Rhodé Rebel (500819128)")
        
    co2 = pd.read_csv('co2.csv')
    woningdichtheid = pd.read_csv('woningdichtheid.csv')
    gemeentegrenzen = pd.read_csv('gemeentegrenzen.csv')
    
    st.subheader("Dataset")
    st.markdown("<p style = 'font-size:20px;'><strong>CO₂-uitstoot</strong> (Klimaatmonitor)</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.5, 1])
    with col1:      
        st.dataframe(co2[['Gemeenten', 'Jaar', 'totaal_co2', 'totaal_co2_ext_weg', 'co2_woningen']].head())
    with col2:
        green_block3("<strong>Omschrijving</strong>", "Deze bewerkte* dataset bevat de totale CO₂-uitstoot, totale CO₂-uitstoot exclusief wegen en CO₂-uitstoot voor woningen in ton per gemeente in Nederland voor 2017, 2018 en 2019.", "Bron: <em>https://klimaatmonitor.databank.nl/jive</em>")
    
    st.markdown("""<hr style="height:5px;border:none;color:rgb(187, 217, 117);background-color:rgb(187, 217, 117);" /> """, unsafe_allow_html=True)
    
    st.subheader("Hulpbronnen")
    st.markdown("<p style = 'font-size:20px;'><strong>Woningdichtheid</strong> (CBS)</p>", unsafe_allow_html=True)
    col3, col4 = st.columns([1, 1.5])
    with col3:
        st.dataframe(woningdichtheid.head())
    with col4:
        green_block3("<strong>Omschrijving</strong>", "Deze bewerkte* dataset bevat de woningdichtheid (aantal woningen per km²) per gemeente in Nederland voor 2017, 2018 en 2019. Deze dataset is verkregen door het aanpassen van de tabel ‘Regionale kerncijfers Nederland’ in StatLine en dient als hulpbron voor de CO₂ dataset.", "Bron: <em>https://opendata.cbs.nl/statline/#/CBS/nl/dataset/70072NED/table?fromstatweb</em>")
    
    st.markdown("<p style = 'font-size:20px;'><strong>Gemeentegrenzen</strong> (CBS)</p>", unsafe_allow_html=True)
    col5, col6 = st.columns([1, 1.5])
    with col5:
        st.dataframe(gemeentegrenzen.head())
    with col6:
        green_block3("<strong>Omschrijving</strong>", "Deze bewerkte* dataset bevat de coördinaten van de grenzen van alle gemeenten in Nederland in 2019 met bijbehorende gemeentecode. De oorspronkelijke coördinaten zijn omgezet naar lengte- en breedtegraden. Deze dataset dient als hulpbron voor de CO₂ dataset.", "Bron: <em>https://www.cbs.nl/nl-nl/onze-diensten/open-data/statline-als-open-data/cartografie</em>")
