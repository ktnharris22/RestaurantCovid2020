#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 19:38:54 2020

@author: javiermac
"""
import requests
import json
import pandas as pd
import numpy as np
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.offline as py 
import plotly.graph_objs as go

def spaces(text):
    return "%20".join(text.split(" "))
    
def coordinates(address):
    address = spaces(address)+'%20Pittsburgh,%20Pennsylvania,%20United%20States'
    address = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + address + ".json?access_token=pk.eyJ1IjoiamFzcmljbyIsImEiOiJjaXc2dHQyeTEwMDNpMnRwMm1wNXZnZHhzIn0.OoPNn5cuLVnaUlrfTiQboQ"
    jsonMapbox = requests.get(address)
    jsonMapbox = jsonMapbox.json()
    coor = pd.DataFrame({'longitude':[jsonMapbox['features'][i]['geometry']['coordinates'][0] 
                                      for i in range(len(jsonMapbox['features']))],
                         'latitude':[jsonMapbox['features'][i]['geometry']['coordinates'][1] 
                                     for i in range(len(jsonMapbox['features']))],
                         'any':['Hi'+str(i)
                                for i in range(len(jsonMapbox['features']))],
                         'val':[i
                                for i in range(len(jsonMapbox['features']))]})
    return coor

"""------- APP------------"""

c = coordinates('Hamburg Hall, Forbes Ave')

mapbox_access_token = 'pk.eyJ1IjoiamFzcmljbyIsImEiOiJjaXc2dHQyeTEwMDNpMnRwMm1wNXZnZHhzIn0.OoPNn5cuLVnaUlrfTiQboQ'

df = pd.read_csv("finalrecycling.csv")

# print(df['boro'][0])
# print(df['longitude'][0])
# print(c['latitude'])

app = dash.Dash(__name__)

blackbold={'color':'black', 'font-weight': 'bold'}

app.layout = html.Div([
#---------------------------------------------------------------
# Map_legen + Borough_checklist + Recycling_type_checklist + Web_link + Map
    html.Div([
        html.Div([
            # Map-legend
            html.Ul([
                html.Li("Compost", className='circle', style={'background': '#ff00ff','color':'black',
                    'list-style':'none','text-indent': '17px'}),
                html.Li("Electronics", className='circle', style={'background': '#0000ff','color':'black',
                    'list-style':'none','text-indent': '17px','white-space':'nowrap'}),
                html.Li("Hazardous_waste", className='circle', style={'background': '#FF0000','color':'black',
                    'list-style':'none','text-indent': '17px'}),
                html.Li("Plastic_bags", className='circle', style={'background': '#00ff00','color':'black',
                    'list-style':'none','text-indent': '17px'}),
                html.Li("Recycling_bins", className='circle',  style={'background': '#824100','color':'black',
                    'list-style':'none','text-indent': '17px'}),
            ], style={'border-bottom': 'solid 3px', 'border-color':'#00FC87','padding-top': '6px'}
            ),

            # Borough_checklist
            html.Label(children=['Borough: '], style=blackbold),
            dcc.Checklist(id='boro_name',
                    options=[{'label':str(b),'value':b} for b in c['any']], #sorted(df['boro'].unique())],
                    value=[b for b in c['val']], #sorted(df['boro'].unique())],
            ),

            # Recycling_type_checklist
            html.Label(children=['Looking to recycle: '], style=blackbold),
            dcc.Checklist(id='recycling_type',
                    options=[{'label':str(b),'value':b} for b in c['any']], #sorted(df['type'].unique())],
                    value=[b for b in c['val']],#sorted(df['type'].unique())],
            ),

            # Web_link
            html.Br(),
            html.Label(['Website:'],style=blackbold),
            html.Pre(id='web_link', children=[],
            style={'white-space': 'pre-wrap','word-break': 'break-all',
                  'border': '1px solid black','text-align': 'center',
                  'padding': '12px 12px 12px 12px', 'color':'blue',
                  'margin-top': '3px'}
            ),

        ], className='three columns'
        ),

        # Map
        html.Div([
            dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
                style={'background':'#00FC87','padding-bottom':'2px','padding-left':'2px','height':'100vh'}
            )
        ], className='nine columns'
        ),

    ], className='row'
    ),

], className='ten columns offset-by-one'
)

#---------------------------------------------------------------
# Output of Graph
@app.callback(Output('graph', 'figure'),
               [Input('boro_name', 'value'),
                 Input('recycling_type', 'value')])

# def update_figure(chosen_boro,chosen_recycling):
def update_figure(chosen_boro,chosen_recycling):
    # df_sub = df[(df['boro'].isin(chosen_boro)) &
    #             (df['type'].isin(chosen_recycling))]
    # print(df_sub)
    c_c = c[(c['any'].isin(chosen_boro)) &
            (c['any'].isin(chosen_recycling))]
    # Create figure
    locations=[go.Scattermapbox(
                    lon = c_c['longitude'],#df_sub['longitude'],
                    lat = c_c['latitude'],#df_sub['latitude'],
                    mode='markers',
                    # marker={'color' : 'green'},#df_sub['color']},
                    unselected={'marker' : {'opacity':1}},
                    selected={'marker' : {'opacity':0.5, 'size':25}}#,
                    # hoverinfo='text',
                    # hovertext=df_sub['hov_txt'],
                    # customdata=df_sub['website']
    )]

    # Return figure
    return {
        'data': locations,
        'layout': go.Layout(
            uirevision= 'foo', #preserves state of figure/map after callback activated
            clickmode= 'event+select',
            hovermode='closest',
            hoverdistance=2,
            title=dict(text="COVID MONITOR - PITTSBURGH RESTAURANTS",font=dict(size=30, color='brown')),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=25,
                style='light',
                center=dict(
                    lat=c[0][1],
                    lon=c[0][0]
                ),
                pitch=40,
                zoom=11.5
            ),
        )
    }
#---------------------------------------------------------------
# callback for Web_link
@app.callback(
    Output('web_link', 'children'))
    # [Input('graph', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        return 'Click on any bubble'
    else:
        # print (clickData)
        the_link=clickData['points'][0]['customdata']
        if the_link is None:
            return 'No Website Available'
        else:
            return html.A(the_link, href=the_link, target="_blank")

# #--------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)

def main(address):
    c = coordinates('Hamburg Hall, Forbes Ave')
    print(c)


# if __name__ == "__main__":
#     main()