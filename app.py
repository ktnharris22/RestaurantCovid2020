import json

mapbox_access_token = 'pk.eyJ1IjoiamFzcmljbyIsImEiOiJjaXc2dHQyeTEwMDNpMnRwMm1wNXZnZHhzIn0.OoPNn5cuLVnaUlrfTiQboQ'

import pandas as pd
import numpy as np
import dash  # (version 1.0.0)
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests
import datetime

import plotly.offline as py  # (version 4.4.1)
import plotly.graph_objs as go

# %%Data Processing
category_cd_list = [117, 118, 201, 202, 203, 211, 212, 250, 407]  # relevant categeory codes
cutoff = datetime.datetime(2018, 1, 1)  # cutoff threshold for recency

map_df = pd.read_csv("RestaurantInspect.csv")
map_df = map_df[map_df['city'] == 'Pittsburgh']
map_df['inspect_dt'] = pd.to_datetime(map_df['inspect_dt'], format='%m/%d/%Y')

map_df = map_df.loc[map_df['inspect_dt'] >= cutoff]  # dataframe of recent inspections in Pittsburgh
map_df = map_df.loc[map_df['category_cd'].isin(
    category_cd_list)]  # dataframe fo recent inspection in Pittsburgh and of relevant categories
map_df['street address'] = map_df['num'] + ' ' + map_df['street'] + ' Pittsburgh, PA ' #+ str(map_df['zip'])

map_df = map_df.drop(columns=['encounter', 'id', 'placard_st', 'bus_st_date', 'category_cd',
                              'start_time', 'end_time', 'municipal', 'ispt_purpose', 'abrv',
                              'reispt_cd', 'reispt_dt', 'num', 'street', 'status', 'zip'])
map_df['street address'].isna

uniq_facs = map_df['facility_name'].unique()

final_map_df = pd.DataFrame(columns=['facility_name', 'Address', 'Latitude', 'Longitude',
                                     'Inspection Date', 'Inspection Status', 'Inspection Purpose',
                                     'Color', 'Hover Text', 'Restaurant Type'])  ##description is restaurant type


# Covid Status - has it been inspected for Covid? Did it pass or fail?
# Inspection Status = placard_desc
# Color = Based off of Inspection Status (placard_desc)
# Inspected & Permitted = Green
# Closure/Imminent Hazard; Ordered to Close; Inspected/Permit Denied; Closure/No Entry = Red
# You are here = Blue
# Consumer Alert; Not Selected = Orange/Yellow;
# Hover Text
# facility name
# date, purpose & result of last inspection
# address


# %%
def findColorCode(inspec_status, covid_inspect):
    color = ''
    if inspec_status == 'Inspected & Permitted':
        if covid_inspect == True:
            color = '#0FFF00'
        else:
            color = '#006600'
    elif inspec_status == 'Consumer Alert' or 'Not Selected':
        color = '#F99505'
    elif inspec_status in (
    'Closure/Imminent Hazard', 'Ordered To Close', 'Inspected/Permit denied', 'Closure/No Entry'):
        if covid_inspect == True:
            color = '#ff0000'
        else:
            color = '#800000'
    return color


for fac in uniq_facs:
    fac_df = map_df.loc[map_df['facility_name'] == fac]
    addresses = fac_df['street address'].dropna().unique()

    for address in addresses:
        uniq_fac_df = fac_df[fac_df['street address'] == address]
        placard_desc = uniq_fac_df['placard_desc'].unique()
        print(f'{fac} {address}')
        most_recent_inspect_dt = max(uniq_fac_df['inspect_dt'])  # find the most recent inspect date
        insp_status = uniq_fac_df['placard_desc'][uniq_fac_df['inspect_dt'] == most_recent_inspect_dt].iloc[0]
        insp_purpose = uniq_fac_df['purpose'][uniq_fac_df['inspect_dt'] == most_recent_inspect_dt].iloc[0]
        covid_inspect = insp_purpose.find('COVID') == 0
        rest_type = uniq_fac_df['description'][uniq_fac_df['inspect_dt'] == most_recent_inspect_dt].iloc[0]
        lat = ''
        long = ''
        colorCode = findColorCode(insp_status, covid_inspect)
        hovText = f'Name:{fac} <br>Address:{address} <br>Most Recent Inspection Date:{most_recent_inspect_dt} Inspection Status:{insp_status} Inspection Purpose:{insp_purpose}'
        final_map_df = final_map_df.append(
            {'facility_name': fac, 'Address': address, 'Latitude': lat, 'Longitude': long,
             'Inspection Status': insp_status, 'Inspection Date': most_recent_inspect_dt,
             'Inspection Purpose': insp_purpose, 'Color': colorCode, 'Restaurant Type': rest_type, 'Hover Text': hovText
             }, ignore_index=True)

print(map_df.shape)

# %%App
app = dash.Dash(__name__)

blackbold = {'color': 'black', 'font-weight': 'bold'}

app.layout = html.Div([
    # ---------------------------------------------------------------
    # Map_legen + Borough_checklist + Recycling_type_checklist + Web_link + Map
    html.Div([
        html.Div([
            # Map-legend
            html.Ul([
                html.Li("Open", className='circle', style={'background': '#0FFF00', 'color': 'black',
                                                           'list-style': 'none', 'text-indent': '17px'}),
                html.Li("Ordered to Close/Closed", className='circle', style={'background': '#FF0049', 'color': 'black',
                                                                              'list-style': 'none',
                                                                
                                                                'text-indent': '17px',
                                                                              'white-space': 'nowrap'}),
                html.Li("You Are Here", className='circle', style={'background': '#0326D1', 'color': 'black',
                                                                   'list-style': 'none', 'text-indent': '17px'}),
                html.Li("Warning", className='circle', style={'background': '#F99505', 'color': 'black',
                                                              'list-style': 'none', 'text-indent': '17px'}),

            ], style={'border-bottom': 'solid 3px', 'border-color': '#00FC87', 'padding-top': '6px'}
            ),

            # Restaurant Category
            html.Label(children=['What kind of restaurant: '], style=blackbold),
            dcc.Checklist(id='restaurant_type',
                          options=[{'label': str(b), 'value': b} for b in sorted(df['description'].unique())],
                          value=[b for b in sorted(df['description'].unique())],
                          ),

        ], className='three columns'
        ),

        # Search Bar
        html.Label(children=['Where are you located?'], style=blackbold),
        html.Div([
            dcc.Input(id='Address', placeholder='5000 Forbes Ave, Pittsburgh, PA 15213', type='text', debounce=True)
        ]),

        # Map
        html.Br(),
        html.Div([
            dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
                      style={'background': '#00FC87', 'padding-bottom': '2px', 'padding-left': '2px',
                             'height': '100vh'}
                      )
        ], className='nine columns'
        ),

    ], className='row'

    ),

], className='ten columns offset-by-one'
)


# ---------------------------------------------------------------
# Output of Graph
@app.callback(Output('graph', 'figure'),
              [Input('zip_name', 'value'),
               Input('restaurant_type', 'value')],
              Input('Address', 'value'))
def update_figure(chosen_zip, chosen_description, input_address):
    df_sub = df[(df['zip'].isin(chosen_zip)) &
                (df['description'].isin(chosen_description))]
    zoom_address = input_address.replace(' ', '%20') if type(input_address) == str \
        else '5000%20Forbes%20Ave.%20Pittsburgh,%20PA'
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{zoom_address}.json?access_token={mapbox_access_token}"
    response = requests.get(url)
    data_json = response.json()
    coordinates = data_json['features'][0]['geometry']['coordinates']
    long = coordinates[0]
    lat = coordinates[1]
    df_sub = df.append({'longitude':long, 'latitude':lat, 'color':'#33FFF0'}, ignore_index = True)

    # Create figure
    locations = [go.Scattermapbox(
        lon=df_sub['longitude'],
        lat=df_sub['latitude'],
        mode='markers',
        marker={'color': df_sub['color'], 'size':20},
        unselected={'marker': {'opacity': 1}},
        selected={'marker': {'opacity': 0.5, 'size': 50}},
        # hoverinfo='text',
        # hovertext=df_sub['hov_txt'], #Pop up message info
        # customdata=df_sub['website']
    )]

    # Return figure
    return {
        'data': locations,
        'layout': go.Layout(
            uirevision='foo',  # preserves state of figure/map after callback activated
            clickmode='event+select',
            hovermode='closest',
            hoverdistance=2,
            title=dict(text="Where to Eat in Pittsburgh?", font=dict(size=50, color='brown')),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=25,
                style='mapbox://styles/jasrico/ckib1pi3b0bce1apg5k54oich',
                center=dict(
                    lat=lat,
                    lon=long
                ),
                pitch=0,
                zoom=15
            ),
        )
    }


# ---------------------------------------------------------------
# callback for Web_link
@app.callback(
    Output('web_link', 'children'),
    [Input('graph', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        return 'Click on any bubble'
    else:
        # print (clickData)
        the_link = clickData['points'][0]['customdata']
        if the_link is None:
            return 'No Website Available'
        else:
            return html.A(the_link, href=the_link, target="_blank")


# #--------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
