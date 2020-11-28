mapbox_access_token = 'pk.eyJ1IjoiamFzcmljbyIsImEiOiJjaXc2dHQyeTEwMDNpMnRwMm1wNXZnZHhzIn0.OoPNn5cuLVnaUlrfTiQboQ'

import pandas as pd
import numpy as np
import dash  # (version 1.0.0)
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.offline as py  # (version 4.4.1)
import plotly.graph_objs as go

df = pd.read_csv("geofoodfacilities.csv")
df = df[df['city'] == 'Pittsburgh']

app = dash.Dash(__name__)

blackbold = {'color': 'black', 'font-weight': 'bold'}

app.layout = html.Div([
    # ---------------------------------------------------------------
    # Map_legen + Borough_checklist + Recycling_type_checklist + Web_link + Map
    html.Div([
        html.Div([
            # Map-legend
            html.Ul([
                html.Li("Open", className='circle', style={'background': '#ff00ff', 'color': 'black',
                                                           'list-style': 'none', 'text-indent': '17px'}),
                html.Li("Ordered to Close/Closed", className='circle', style={'background': '#0000ff', 'color': 'black',
                                                                              'list-style': 'none',
                                                                              'text-indent': '17px',
                                                                              'white-space': 'nowrap'}),
                html.Li("Delivers", className='circle', style={'background': '#FF0000', 'color': 'black',
                                                               'list-style': 'none', 'text-indent': '17px'}),
                html.Li("Warning", className='circle', style={'background': '#00ff00', 'color': 'black',
                                                              'list-style': 'none', 'text-indent': '17px'}),

            ], style={'border-bottom': 'solid 3px', 'border-color': '#00FC87', 'padding-top': '6px'}
            ),

            #
            html.Label(children=['zip: '], style=blackbold),
            dcc.Checklist(id='zip_name',
                          options=[{'label': str(b), 'value': b} for b in sorted(df['zip'].unique())],
                          value=[b for b in sorted(df['zip'].unique())],
                          ),

            # Restaurant Category
            html.Label(children=['What kind of restaurant: '], style=blackbold),
            dcc.Checklist(id='restaurant_type',
                          options=[{'label': str(b), 'value': b} for b in sorted(df['description'].unique())],
                          value=[b for b in sorted(df['description'].unique())],
                          ),

            # Web_link
            html.Br(),
            html.Label(['Website:'], style=blackbold),
            html.Pre(id='web_link', children=[],
                     style={'white-space': 'pre-wrap', 'word-break': 'break-all',
                            'border': '1px solid black', 'text-align': 'center',
                            'padding': '12px 12px 12px 12px', 'color': 'blue',
                            'margin-top': '3px'}
                     ),

        ], className='three columns'
        ),

        # Search Bar
        html.Label(children=['Where are you located?'], style=blackbold),
        html.Div([
            dcc.Input(id='Address', placeholder='5000 Forbes Ave, Pittsburgh, PA 15213', type='text', debounce=True)
        ]),

        # Map
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
               Input('restaurant_type', 'value')]
            )

def update_figure(chosen_zip, chosen_description):
    df_sub = df[(df['zip'].isin(chosen_zip)) &
                (df['description'].isin(chosen_description))]

    # Create figure
    locations = [go.Scattermapbox(
        lon=df_sub['longitude'],
        lat=df_sub['latitude'],
        mode='markers',
        # marker={'color': df_sub['color']},
        unselected={'marker': {'opacity': 1}},
        selected={'marker': {'opacity': 0.5, 'size': 25}},
        # hoverinfo='text',
        # hovertext=df_sub['hov_txt'],
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
            title=dict(text="Where to eat in Pittsburgh?", font=dict(size=50, color='red')),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=25,
                style='light',
                center=dict(
                    lat=40.440624,
                    lon=-79.99588
                ),
                pitch=40,
                zoom=11.5
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
