mapbox_access_token = 'pk.eyJ1IjoiamFzcmljbyIsImEiOiJjaXc2dHQyeTEwMDNpMnRwMm1wNXZnZHhzIn0.OoPNn5cuLVnaUlrfTiQboQ'
import pandas as pd
import dash  # (version 1.0.0)
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests
import datetime
import plotly.graph_objs as go

# %%Data Processing
category_cd_list = [117, 118, 201, 202, 203, 211, 212, 250, 407]  # relevant categeory codes
cutoff = datetime.datetime(2018, 1, 1)  # cutoff threshold for recency

rest_inspect_df = pd.read_csv("RestaurantInspect.csv")
rest_inspect_df = rest_inspect_df[rest_inspect_df['city'] == 'Pittsburgh']
rest_inspect_df['inspect_dt'] = pd.to_datetime(rest_inspect_df['inspect_dt'], format='%m/%d/%Y')

rest_inspect_df = rest_inspect_df.loc[rest_inspect_df['inspect_dt'] >= cutoff]  # dataframe of recent inspections in Pittsburgh
rest_inspect_df = rest_inspect_df.loc[rest_inspect_df['category_cd'].isin(category_cd_list)]  # dataframe fo recent inspection in Pittsburgh and of relevant categories
rest_inspect_df['street_address'] = rest_inspect_df['num'] + ' ' + rest_inspect_df['street'] + ' Pittsburgh, PA ' #+ str(rest_inspect_df['zip'])

rest_inspect_df = rest_inspect_df.drop(columns=['encounter', 'id', 'placard_st', 'bus_st_date', 'category_cd',
                              'start_time', 'end_time', 'municipal', 'ispt_purpose', 'abrv',
                              'reispt_cd', 'reispt_dt', 'num', 'street', 'status', 'zip'])
rest_inspect_df.sort_values(by=['inspect_dt','street_address'], ascending=False, inplace=True) #sort dataframe so the most recent inspection of every restarurant is on top
print(f'rest_inspect_df Before drop {rest_inspect_df.shape}')
rest_inspect_df.drop_duplicates(subset=['street_address'], inplace=True, keep='first') #drop duplicates, and keep only the most recent inspection of a restaurant
print(f'rest_inspect_df After drop {rest_inspect_df.shape}')
rest_inspect_df.dropna(subset=['street_address'],inplace=True)
print(f'rest_inspect_df After dropna {rest_inspect_df.shape}')

#ProcessGeoFoodFacs.csv
category_cd_list = [117, 118, 201, 202, 203, 211, 212, 250, 407]  # relevant categeory codes
cutoff = datetime.datetime(2018, 1, 1)  # cutoff threshold for recency

geo_df = pd.read_csv("geofoodfacilities.csv")
geo_df = geo_df[geo_df['city'] == 'Pittsburgh']
#geo_df['inspect_dt'] = pd.to_datetime(rest_inspect_df['inspect_dt'], format='%m/%d/%Y')

#geo_df = geo_df.loc[geo_df['inspect_dt'] >= cutoff]  # dataframe of recent inspections in Pittsburgh
geo_df = geo_df.loc[geo_df['category_cd'].isin(category_cd_list)]  # dataframe fo recent inspection in Pittsburgh and of relevant categories
geo_df['street_address'] = geo_df['num'] + ' ' + geo_df['street'] + ' Pittsburgh, PA ' #+ str(rest_inspect_df['zip'])

geo_df = geo_df.drop(columns=['id', 'num', 'street', 'city', 'state', 'municipal', 'category_cd', 'description', 'p_code', 'fdo',
                              'bus_st_date', 'bus_cl_date', 'seat_count', 'noroom', 'sq_feet', 'status', 'placard_st', 'status', 'zip'])
print(f'geo_df before dropna {geo_df.shape}')
geo_valid = geo_df.dropna()
print(f'geo_df After dropna {geo_valid.shape}')
geo_valid.drop_duplicates(subset=['street_address','longitude','latitude'], inplace=True, keep='first')
print(f'geo_df After drop dups {geo_valid.shape}')

#Merge
merge_df = pd.merge(rest_inspect_df, geo_valid, on=['street_address','facility_name'], how='left', validate="1:1")
merge_df = merge_df.set_index('street_address')

print(f"After merge of geo_df and rest_df there are {merge_df['latitude'].isna().sum()} na coordinates")

map_quest_df = pd.read_csv('AddressesLongLat.csv')
map_quest_df = map_quest_df[map_quest_df['Neighborhood'].notna()]
map_quest_df = map_quest_df.set_index('street_address')

#replace longitude latitude not found in geofoodfacilities.csv with <long, lat> found by mapquest api if exists
no_address_merge_df = merge_df[merge_df['latitude'].isna() == True]
for address in no_address_merge_df.index.to_numpy():
    if address in map_quest_df.index.to_numpy():
        #print(f'Address found {address}')
        long = map_quest_df.at[address, 'Longitude']
        merge_df.at[address, 'longitude'] = long
        lat = map_quest_df.at[address, 'Latitude']
        merge_df.at[address, 'latitude'] = lat

print(f"After lookup there are {merge_df['latitude'].isna().sum()} na coordinates")

#%%
#uniq_facs = rest_inspect_df['facility_name'].unique()

#map_df = pd.DataFrame(columns=['facility_name', 'street address', 'Inspection Date',
                                     #'Inspection Status', 'Inspection Purpose',
                                     #'Restaurant Type'])  ##description is restaurant type


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
Closed = ['Closure/Imminent Hazard', 'Inspected/Permit denied', 'Ordered To Close']
ConsumerAlert = ['Consumer Alert', 'Not Selected']

def findColorCode(inspec_status, covid_inspect):
    color = ''
    if inspec_status == 'Inspected & Permitted':
        if covid_inspect == True:
            color = '#0FFF00'
        else:
            color = '#006600'
    if inspec_status in ConsumerAlert:
        color = '#F99505'
    if inspec_status in Closed:
        if covid_inspect == True:
            color = '#ff0000'
        else:
            color = '#800000'
    return color
colors = []
HoverText = []
for index, row in merge_df.iterrows():
    #print(index)
    covid_inspect = row['purpose'].find('COVID') == 0
    colorCode = findColorCode(row['placard_desc'], covid_inspect)
    hovText = f"Name: {row['facility_name']} <br>Address: {index} <br>Most Recent Inspection Date:{row['inspect_dt']} <br>Inspection Status:{row['placard_desc']} Inspection Purpose:{row['purpose']}"
    colors.append(colorCode)
    HoverText.append(hovText)

merge_df['Colors'] = colors
merge_df['Hover Text'] = HoverText

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
# address_df = pd.DataFrame(columns=['street_address', 'Latitude', 'Longitude', 'Neighborhood'])
# uniq_add = map_df['Address'].dropna().unique()
# #address_df = address_df.append({'street_address': 'Address', 'Latitude': 'Latitude',
# #                   'Longitude': 'Longitude', 'Neighborhood': 'Neighborhood'}, ignore_index=True)
#
# for add in uniq_add:
#     d = geolocateAddress(add)
#     address_df = address_df.append({'street_address': add, 'Latitude': d['lat'],
#                                     'Longitude': d['lng'], 'Neighborhood': d['Neighborhood']}, ignore_index=True)
#     print(add)
# address_df.to_csv('AddressesLongLat.csv', index=False, header=True)



#%%
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
                          options=[{'label': str(b), 'value': b} for b in sorted(merge_df['description'].unique())],
                          value=[b for b in sorted(merge_df['description'].unique())],
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
    df_sub = merge_df[(merge_df['description'].isin(chosen_type))]
    zoom_address = input_address.replace(' ', '%20') if type(input_address) == str \
        else '5000%20Forbes%20Ave.%20Pittsburgh,%20PA'
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{zoom_address}.json?access_token={mapbox_access_token}"
    response = requests.get(url)
    data_json = response.json()
    coordinates = data_json['features'][0]['geometry']['coordinates']
    long = coordinates[0]
    lat = coordinates[1]
    df_sub = df_sub.append({'longitude':long, 'latitude':lat, 'Colors': '#0326D1', 'Hover Text': 'YOU ARE HERE'}, ignore_index = True)

    # Create figure
    locations = [go.Scattermapbox(
        lon=df_sub['longitude'],
        lat=df_sub['latitude'],
        mode='markers',
        marker={'color': df_sub['Colors'], 'size':10},
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
                style='streets', #'mapbox://styles/jasrico/ckib1pi3b0bce1apg5k54oich',
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
