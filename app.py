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

map_lat_long = pd.read_csv("AddressesLongLat.csv")
map_lat_long = map_lat_long[map_lat_long['Longitude'] > -82]
col = map_lat_long.Address.str.split(expand=True)
col[3] = col[3].map(lambda x: x.lstrip(',').rstrip(','))
col.rename(columns={0:"num",3:"city",4:"state"},inplace=True)
col["street"] = col[1]+" "+col[2]
col[["latitude","longitude","address"]] = map_lat_long[["Latitude","Longitude","Address"]]
col.drop(col.columns[[1,2,5,6,7,8]],axis=1,inplace=True)

map_df = pd.read_csv("RestaurantInspect.csv")
map_df = map_df[map_df['city'] == 'Pittsburgh']
# print(map_df[["facility_name","inspect_dt","category_cd","placard_desc"]])
# col["facility_name"]=
map_df["entireaddress"]=map_df["num"]+map_df["street"]+map_df["city"]
map_df["entireaddress"]=map_df["entireaddress"].str.replace(" ","")
col["entireaddress"]=col["num"]+col["street"]+col["city"]
col["entireaddress"] = col["entireaddress"].str.replace(" ","")
# print(map_df["entireaddress"])

map_df_1 = pd.merge(map_df, col, left_on='entireaddress', right_on='entireaddress',how='left')
map_df_1=map_df_1[pd.notnull(map_df_1.longitude)]
map_df_1[['num', 'street','city', 'state']]=map_df_1[['num_x', 'street_x','city_x', 'state_x']]
map_df = map_df_1.drop(columns=['num_x', 'street_x','city_x', 'state_x',
                                  'num_y', 'street_y','city_y', 'state_y'])

# print(map_df[["facility_name","latitude","longitude","placard_desc","inspect_dt",'purpose']][map_df["facility_name"] == "Stuff'd Pierogi Bar"])
# print(map_df[["facility_name","latitude","longitude","placard_desc","inspect_dt",'purpose']][map_df["facility_name"] == "Seven"])
print(map_df[["latitude","longitude"]][map_df["facility_name"] == "Stuff'd Pierogi Bar"])
print(map_df[["latitude","longitude"]][map_df["facility_name"] == "Seven"])


map_df['inspect_dt'] = pd.to_datetime(map_df['inspect_dt'], format='%m/%d/%Y')

map_df = map_df.loc[map_df['inspect_dt'] >= cutoff]  # dataframe of recent inspections in Pittsburgh
map_df = map_df.loc[map_df['category_cd'].isin(category_cd_list)]  # dataframe fo recent inspection in Pittsburgh and of relevant categories
map_df['street address'] = map_df['num'] + ' ' + map_df['street'] + ' Pittsburgh, PA ' #+ str(map_df['zip'])

map_df = map_df.drop(columns=['encounter', 'placard_st', 'bus_st_date', 'category_cd',
                              'start_time', 'end_time', 'municipal', 'ispt_purpose', 'abrv',
                              'reispt_cd', 'reispt_dt', 'num', 'street', 'status', 'zip'])
#%%
uniq_facs = map_df['facility_name'].unique()

final_map_df = pd.DataFrame(columns=['facility_name', 'street address', 'Inspection Date',
                                     'Inspection Status', 'Inspection Purpose',
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

def findColorCode(inspec_status, covid_inspect):
    color = ''
    if inspec_status == 'Inspected & Permitted':
        if covid_inspect == True:
            color = '#0FFF00'
        else:
            color = '#006600'
    elif inspec_status == 'Consumer Alert' or 'Not Selected':
        color = '#F99505'
    elif inspec_status == 'Closure/Imminent Hazard' or 'Ordered To Close' or 'Inspected/Permit denied' or 'Closure/No Entry' or 'Closure/Unpaid Fees':
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
        # print(f'{fac} {address}')
        most_recent_inspect_dt = max(uniq_fac_df['inspect_dt'])  # find the most recent inspect date
        insp_status = uniq_fac_df['placard_desc'][uniq_fac_df['inspect_dt'] == most_recent_inspect_dt].iloc[0]
        insp_purpose = uniq_fac_df['purpose'][uniq_fac_df['inspect_dt'] == most_recent_inspect_dt].iloc[0]
        covid_inspect = insp_purpose.find('COVID') == 0
        rest_type = uniq_fac_df['description'][uniq_fac_df['inspect_dt'] == most_recent_inspect_dt].iloc[0]
        colorCode = findColorCode(insp_status, covid_inspect)
        hovText = f'Name:{fac} <br>Address:{address} <br>Most Recent Inspection Date:{most_recent_inspect_dt} Inspection Status:{insp_status} Inspection Purpose:{insp_purpose}'
        final_map_df = final_map_df.append(
            {'facility_name': fac, 'street address': address,
             'Inspection Status': insp_status, 'Inspection Date': most_recent_inspect_dt,
             'Inspection Purpose': insp_purpose, 'Color': colorCode, 'Restaurant Type': rest_type, 'Hover Text': hovText
             }, ignore_index=True)

#%% find addresses with missing lat long

def geolocateAddress(address):
    add = address.replace(' ', '+')
    key = '3btvRc91ydEdr1jO9cM86uNy29iT2kme'
    url = f'http://open.mapquestapi.com/geocoding/v1/address?key={key}&location={add}'
    resp = requests.get(url)
    resp_json = resp.json()
    resp_json = resp_json['results']
    d = resp_json[0]['locations'][0]['latLng']
    d['Neighborhood'] = resp_json[0]['locations'][0]['adminArea6']
    return d
# address_df = pd.DataFrame(columns=['Address', 'Latitude', 'Longitude', 'Neighborhood'])
# uniq_add = final_map_df['Address'].dropna().unique()
# #address_df = address_df.append({'Address': 'Address', 'Latitude': 'Latitude',
# #                   'Longitude': 'Longitude', 'Neighborhood': 'Neighborhood'}, ignore_index=True)
#
# for add in uniq_add:
#     d = geolocateAddress(add)
#     address_df = address_df.append({'Address': add, 'Latitude': d['lat'],
#                                     'Longitude': d['lng'], 'Neighborhood': d['Neighborhood']}, ignore_index=True)
#     print(add)
# address_df.to_csv('AddressesLongLat.csv', index=False, header=True)


#%%ProcessGeoFoodFacs.csv
category_cd_list = [117, 118, 201, 202, 203, 211, 212, 250, 407]  # relevant categeory codes
cutoff = datetime.datetime(2018, 1, 1)  # cutoff threshold for recency

geo_df = pd.read_csv("geofoodfacilities.csv")
geo_df = geo_df[geo_df['city'] == 'Pittsburgh']
#geo_df['inspect_dt'] = pd.to_datetime(map_df['inspect_dt'], format='%m/%d/%Y')

#geo_df = geo_df.loc[geo_df['inspect_dt'] >= cutoff]  # dataframe of recent inspections in Pittsburgh
geo_df = geo_df.loc[geo_df['category_cd'].isin(category_cd_list)]  # dataframe fo recent inspection in Pittsburgh and of relevant categories
geo_df['street address'] = geo_df['num'] + ' ' + geo_df['street'] + ' Pittsburgh, PA ' #+ str(map_df['zip'])

geo_df = geo_df.drop(columns=['num', 'street', 'city', 'state', 'municipal', 'category_cd', 'description', 'p_code', 'fdo',
                              'bus_st_date', 'bus_cl_date', 'seat_count', 'noroom', 'sq_feet', 'status', 'placard_st', 'status', 'zip'])
geo_valid = geo_df[geo_df['longitude'].notna()]


geo_valid = geo_valid.drop(columns=['id'])
geo_valid = geo_valid.append(map_df,ignore_index = True)


merge_df = pd.merge(final_map_df, geo_valid, on='street address', how='left')


# App
app = dash.Dash(__name__)

blackbold = {'color': 'black', 'font-weight': 'bold'}

app.layout = html.Div([
    # ---------------------------------------------------------------
    # Map_legen + Borough_checklist + Recycling_type_checklist + Web_link + Map
    html.Div([
        html.Div([
            # Map-legend
            html.Ul([
                html.Li("Open and Already Inspected for COVID", className='circle',
                        style={'background': '#0FFF00', 'color': 'black',
                                                           'list-style': 'none', 'text-indent': '17px'}),
                html.Li("Open and Not Inspected for COVID", className='circle',
                        style={'background': '#006600', 'color': 'black',
                               'list-style': 'none', 'text-indent': '17px'}),
                html.Li("Ordered to Close/Closed because of COVID", className='circle',
                        style={'background': '#ff0000', 'color': 'black', 'list-style': 'none',
                        'text-indent': '17px', 'white-space': 'nowrap'}),
                html.Li("Ordered to Close/Closed NOT because of COVID", className='circle',
                        style={'background': '#800000', 'color': 'black', 'list-style': 'none',
                               'text-indent': '17px', 'white-space': 'nowrap'}),
                html.Li("You Are Here", className='circle', style={'background': '#0326D1', 'color': 'black',
                                                                   'list-style': 'none', 'text-indent': '17px'}),
                html.Li("Warning", className='circle', style={'background': '#F99505', 'color': 'black',
                                                              'list-style': 'none', 'text-indent': '17px'}),

            ], style={'border-bottom': 'solid 3px', 'border-color': '#00FC87', 'padding-top': '6px'}
            ),

            # Restaurant Category
            html.Label(children=['What kind of restaurant: '], style=blackbold),
            dcc.Checklist(id='restaurant_type',
                          options=[{'label': str(b), 'value': b} for b in sorted(merge_df['Restaurant Type'].unique())],
                          value=[b for b in sorted(merge_df['Restaurant Type'].unique())],
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
              [Input('restaurant_type', 'value')],
              Input('Address', 'value'))
def update_figure(chosen_type, input_address):
    df_sub = merge_df[(merge_df['Restaurant Type'].isin(chosen_type))]
    zoom_address = input_address.replace(' ', '%20') if type(input_address) == str \
        else '5000%20Forbes%20Ave.%20Pittsburgh,%20PA'
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{zoom_address}.json?access_token={mapbox_access_token}"
    response = requests.get(url)
    data_json = response.json()
    coordinates = data_json['features'][0]['geometry']['coordinates']
    long = coordinates[0]
    lat = coordinates[1]
    df_sub = df_sub.append({'longitude':long, 'latitude':lat, 'color':'#33FFF0'}, ignore_index = True)

    # Create figure
    locations = [go.Scattermapbox(
        lon=df_sub['longitude'],
        lat=df_sub['latitude'],
        mode='markers',
        marker={'color': df_sub['Color'], 'size':10},
        unselected={'marker': {'opacity': 1}},
        selected={'marker': {'opacity': 0.5, 'size': 50}},
        hoverinfo='text',
        hovertext=df_sub['Hover Text'], #Pop up message info
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

# #--------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
