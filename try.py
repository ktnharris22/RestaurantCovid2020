#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 15:37:00 2020

@author: javiermac
"""


import pandas as pd

def runit(pattern, s):
    for a in s:
        if re.search(pattern, a) != None:
            print(a)

def spaces(text):
    return "%20".join(text.split(" "))

map_lat_long = pd.read_csv("AddressesLongLat.csv")
map_lat_long = map_lat_long[map_lat_long['Longitude'] > -82]
col = map_lat_long.Address.str.split(expand=True)
col[3] = col[3].map(lambda x: x.lstrip(',').rstrip(','))
col.rename(columns={0:"num",3:"city",4:"state"},inplace=True)
col["street"] = col[1]+" "+col[2]
col[["latitude","longitude","address"]] = map_lat_long[["Latitude","Longitude","Address"]]
col.drop(col.columns[[1,2,5,6,7,8]],axis=1,inplace=True)
# print(map_lat_long)
# intersection=pd.merge(map_df, col, how='inner',on=["num", "city", "state", "street"])
# union=pd.merge(map_df, col, how='outer',on=["num", "city", "state", "street"])
# map_df = union - intersection

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


# map_df_1=pd.merge(map_df,custocolmer,on='entireaddress',how='outer')
map_df_4=pd.DataFrame()
map_df_4[['facility_name', 'longitude', 'latitude', 'address']] = \
    map_df_1[['facility_name', 'longitude', 'latitude', 'address']]

map_df_4[["street address"]] = map_df_1["num_x"] + ' ' + map_df_1["street_x"] + " Pittsburgh, PA "
map_df_4["placard_desc"]=map_df_1["placard_desc"]
map_df_4=map_df_4[pd.notnull(map_df_4.longitude)]
map_df_4=map_df_4[pd.notnull(map_df_4.facility_name)]

print(map_df.columns)
print(map_df["longitude"])
# print(len(map_df_4["facility_name"].unique()))

geo_df_2 = pd.read_csv("geofoodfacilities.csv")
geo_df_2 = geo_df_2[geo_df_2['city'] == 'Pittsburgh']
geo_df_2[["street address"]] = geo_df_2["num"] + ' ' + geo_df_2["street"] + " Pittsburgh, PA "
geo_df=pd.DataFrame()
geo_df[['facility_name', 'longitude', 'latitude', 'address','street address']]=\
    geo_df_2[['facility_name', 'longitude', 'latitude', 'address','street address']]
geo_df = geo_df.append(map_df_4,ignore_index = True)
print(map_df["placard_desc"].unique())
print(map_df[["facility_name"]][map_df["placard_desc"]=="Closure/No Entry"])

# geo_df_2["entireaddress"]=geo_df_2["facility_name"]+geo_df_2["num"]+geo_df_2["street"]+geo_df_2["city"]
# geo_df_2["entireaddress"] = geo_df_2["entireaddress"].str.replace(" ","")
# geo_df = pd.merge(map_df_1, geo_df_2, left_on='entireaddress', right_on='entireaddress',how='inner')

# geo_df = geo_df_2["facility_name","inspect_dt","category_cd","placard_desc"]

# print(len(geo_df))

# geo_df = geo_df[geo_df["longitude"]!=""]
# geo_df = geo_df.dropna(axis=0, subset=['longitude'])
# geo_df = pd.notnull(geo_df['longitude'])
# geo_df[~geo_df["longitude"].isnull()]
# geo_df=geo_df[pd.notnull(geo_df.longitude)]
# print(geo_df.columns)
# print(map_df_1.columns)
# print(geo_df_2.columns)
# print(len(geo_df),len(map_df_1),len(geo_df_2))

# map_df = pd.merge(col, geo_df, left_index=True, right_index=True, how='outer')
# print(map_df)

# category_cd_list = [117, 118, 201, 202, 203, 211, 212, 250, 407]  # relevant categeory codes
#
# geo_df = pd.read_csv("geofoodfacilities.csv")
# geo_df = geo_df[geo_df['city'] == 'Pittsburgh']
# #geo_df['inspect_dt'] = pd.to_datetime(map_df['inspect_dt'], format='%m/%d/%Y')
#
# #geo_df = geo_df.loc[geo_df['inspect_dt'] >= cutoff]  # dataframe of recent inspections in Pittsburgh
# geo_df = geo_df.loc[geo_df['category_cd'].isin(category_cd_list)]  # dataframe fo recent inspection in Pittsburgh and of relevant categories
# geo_df['street address'] = geo_df['num'] + ' ' + geo_df['street'] + ' Pittsburgh, PA ' #+ str(map_df['zip'])
#
# geo_df = geo_df.drop(columns=['num', 'street', 'city', 'state', 'municipal', 'category_cd', 'description', 'p_code', 'fdo',
#                               'bus_st_date', 'bus_cl_date', 'seat_count', 'noroom', 'sq_feet', 'status', 'placard_st', 'status', 'zip'])
# geo_valid = geo_df[geo_df['longitude'].notna()]
# # merge_df = pd.merge(final_map_df, geo_valid, on='street address', how='left')
# print(geo_valid.columns)