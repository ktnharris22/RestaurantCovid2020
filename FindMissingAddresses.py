import requests
import pandas as pd


def getMissingCoordinatesDF(addresList, nameOfCSVOUT):
    address_df = pd.DataFrame()
    for add in addresList:
        d = geolocateAddress(add)
        address_df = address_df.append({'street_address': add, 'Latitude': d['lat'],
                                        'Longitude': d['lng'], 'Neighborhood': d['Neighborhood']}, ignore_index=True)
    # print(add)
    address_df.to_csv(f'{nameOfCSVOUT}.csv', index=False, header=True)
    return address_df


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