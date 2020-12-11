import pandas as pd
import datetime
from geopy import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings



def getStats():
    #ignore warnings for setting on a copy. I know I'm working with dataframe slices
    warnings.filterwarnings(action='ignore')

    #set window parameters for graphing
    large = 22;
    med = 16;
    small = 12
    params = {'axes.titlesize': large,
              'legend.fontsize': med,
              'figure.figsize': (18, 10),
              'axes.labelsize': med,
              'axes.titlesize': med,
              'xtick.labelsize': med,
              'ytick.labelsize': med,
              'figure.titlesize': large}
    plt.rcParams.update(params)
    plt.style.use('seaborn-whitegrid')
    sns.set_style("white")


    #dataframes for every breakdown I want to study
    restaurant_df = pd.read_csv("PittsburghRestData.csv")  # full restaurants file
    geocodes_df = pd.read_csv("geocodes.csv")  # full geocoded file
    covidabrvs = ['Covid-19 Assessment', 'Covid-19, Ini', 'Covid-19', 'Covid-19, Complaint']
    covid_df = restaurant_df.loc[restaurant_df['abrv'].isin(covidabrvs)]  # COVID dataframe
    pitt_df = restaurant_df.loc[restaurant_df['city'] == 'Pittsburgh']  # All Pittsburgh dataframe
    pitt_df['inspect_dt'] = pd.to_datetime(pitt_df['inspect_dt'],
                                           format='%m/%d/%Y')  # change inspect date from string to date time
    category_cd_list = [117, 118, 201, 202, 203, 211, 212, 250, 407]  # relevant categeory codes
    cutoff = datetime.datetime(2018, 1, 1)  # cutoff threshold for recency
    pitt_recent_df = pitt_df.loc[pitt_df['inspect_dt'] >= cutoff]  # dataframe of recent inspections in Pittsburgh
    pitt_covid_df = covid_df.loc[covid_df['city'] == 'Pittsburgh']  # Pittsburgh COVID dataframe



    # CREATE ADDRESS FIELD TO BE USED FOR GEOCODES

    geoloc = ''
    locationlist = []
    geolocator = Nominatim(user_agent="myGeocoder")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    #combine pieces of address column into a single column for geocode dataframe

    for index, row in geocodes_df.iterrows():
        if str(row['zip']) == 'nan':
            row['zip'] = 0
        geoloc = str(row['num']) + " " + str(row['street']) + " " + str(row['city']) + " " + str(row['state']) + " " + str(
            int(row['zip']))
        locationlist.append(geoloc)

    geocodes_df['Address'] = locationlist

    geoloc = ''
    locationlist = []

    #combine pieces of address column into a single column for recent inspections dataframe

    for index, row in pitt_recent_df.iterrows():
        geoloc = str(row['num']) + " " + str(row['street']) + " " + row['city'] + " " + row['state'] + " " + str(
            int(row['zip']))
        locationlist.append(geoloc)

    pitt_recent_df['Address'] = locationlist
    pitt_r_geocodes_df = geocodes_df.loc[geocodes_df['Address'].isin(locationlist)]
    uniqueadr = pitt_recent_df['Address'].unique()
    unique_df = pitt_recent_df.loc[pitt_recent_df['Address'].isin(uniqueadr)]

    # Create relevant categories dataframe for graphing and test

    relevant_df = pitt_recent_df.loc[pitt_recent_df['category_cd'].isin(
        category_cd_list)]  # dataframe fo recent inspection in Pittsburgh and of relevant categories
    relevant_closures_df = relevant_df[relevant_df['placard_st'] == 6]  # All relevant Pittsburgh closures
    relevant_covid_df = relevant_df.loc[
        relevant_df['abrv'].isin(covidabrvs)]  # COVID dataframe of restaurants with given categories and recency threshold
    relevant_covid_df_alt = pitt_covid_df.loc[pitt_covid_df['category_cd'].isin(
        category_cd_list)]  # COVID dataframe of restaurants with given categories and recency threshold
    placlist = np.unique(relevant_covid_df['placard_desc'])
    relevant_placs = np.unique(relevant_df['placard_desc'])
    placcolors = [plt.cm.tab10(i / float(len(placlist) - 1)) for i in range(len(placlist))]



    #Drop all other column from the geocodes dataframe to maerge with master

    pitt_r_geocodes_df = pitt_r_geocodes_df.drop(["id", "facility_name", "state", "street", "city"], axis=1)
    pitt_r_geocodes_df = pitt_r_geocodes_df.drop(["num", "municipal", "category_cd", "description", "p_code"], axis=1)
    pitt_r_geocodes_df = pitt_r_geocodes_df.drop(["fdo", "bus_st_date", "bus_cl_date", "seat_count", "noroom"], axis=1)
    pitt_r_geocodes_df = pitt_r_geocodes_df.drop(["sq_feet", "status", "placard_st", "address", "zip"], axis=1)

    #merge with master
    pitt_recent_geo_df = pitt_recent_df.merge(right=pitt_r_geocodes_df,
                                              how='left',  # if an entry is in A, but not in B, add NA values
                                              on=[ "Address"])
    #  )


    #pitt_recent_geo_df.to_csv(index=False)


    # Converts start_time and end_time fields from string to datetime
    # then creates a list of start times and a list of end times

    def timeConversion(given_df):
        given_df['end_time'] = pd.to_datetime(given_df['end_time'], format='%H:%M:%S')
        given_df['start_time'] = pd.to_datetime(given_df['start_time'], format='%H:%M:%S')

        given_start_times = given_df['start_time'].tolist()
        given_end_times = given_df['end_time'].tolist()

        given_insp_dat = [] #cleaned data list
        dirty_insp_dat = [] #unleaned data list
        count = 0

    #Iterate through list of start times subtract start from end time and append to list,
        # one for uncleaned data and one cleaned data

        for t in given_start_times:
            duration = given_end_times[count] - t
            dirty_insp_dat.append(duration)
            if duration.total_seconds() >= 0:
                given_insp_dat.append(duration)
            count += 1

        #convert dirty data list for inspecion diration into series and place it back into dataframe
        #so no data is lost

        se = pd.Series(dirty_insp_dat)
        given_df['inspect_dur'] = se.values

        total = datetime.timedelta(0) #create empty time delta object for total duration time


        for t in given_insp_dat: # set total to cleaned inspection  duration data
            total = total + t

        #now for some math, as not to eliminate or disturb data in original dataframe I ran the math on lists
        # I created of cleaned data

        avg_inspect_time = total / len(given_insp_dat) # average inspection duration
        num_inspections = len(given_insp_dat) # total inspections
        bad_dat = len(given_start_times) - len(given_insp_dat) # data not included in average
        avg_inspect_time = avg_inspect_time - datetime.timedelta(microseconds=avg_inspect_time.microseconds) # removal of micrseconds
        format_avg = str(avg_inspect_time).split(".")[0].split(":") # print formatting
        obsv = len(given_start_times)

        #Printed out summary of results

        print("Average time of Inspection: " + format_avg[1] + " minutes " + format_avg[2] + " seconds ")
        print("Number of inspections by Health Department: " + str(obsv))
        print("Inspections included in average: " + str(num_inspections))
        print("Faulty data removed from operation: " + str(bad_dat))

        return given_df #send back the manipulated dataframe with a new inspection duration column without
                        #disturbing exisitng data in the dataframe


    divider = "-" * 50 # format

    #Prints for dataframes that correspond to potentially intersting categories

    print("\nAll COVID-19 inspections in Pittsburgh city limits: ")
    print(divider)
    pitt_covid_df = timeConversion(pitt_covid_df)

    print("\nAll inspections in Pittsburgh city limits of Queen Beysian's chosen facility types ")
    print(divider)
    relevant_df = timeConversion(relevant_df)

    print("\nCOVID-19 Inspections in Pittsburgh city limits of Queen Beysian's chosen facility types")
    print(divider)
    relevant_covid_df = timeConversion(relevant_covid_df)


    # set inspect date to usable datetime format
    pitt_df['inspect_dt'] = pd.to_datetime(pitt_df['inspect_dt'], format='%m/%d/%Y')



    # GRAPHING---------------------------------------------------------

    # create a column of string versions of the zipcode for graphing
    relevant_covid_df["inspect_dur"] = relevant_covid_df["inspect_dur"].astype('timedelta64[s]') / 60
    relevant_covid_df["zipstr"] = relevant_covid_df["zip"].astype('int').astype('str')


    # Graph of Covid Inspections duration
    def covidInspectTimeGraph(relevant_covid_df):
        colors = [(.9, 0, 0, 1.0),
                  (.8, .7, 0, 1.0),
                  (0.1, 0.9, 0.15, 1.0)]
        plt.figure(figsize=(20, 12), dpi=80, facecolor='w', edgecolor='k')

        for i, plac in enumerate(placlist):
            plt.scatter('zipstr', 'inspect_dur',
                    data=relevant_covid_df.loc[relevant_covid_df.placard_desc == plac, :],
                    s=30, c=colors[i], label=str(plac))

        # Formatting
        plt.gca().set(xlim=(-1, 40), ylim=(0, 180),
                  xlabel='ZipCode', ylabel='Inspection Duration (mins)', )
        plt.xticks(rotation=45)

        plt.xticks(fontsize=12);
        plt.yticks(fontsize=12)
        plt.title("Scatterplot of Pittsburgh COVID Inspections by Zipcode", fontsize=22)
        plt.legend(fontsize=12)
        plt.show()

    # Inspections by Zipcode

    #Same conversion of zipcode for dataframe of closed resaturants,
    # convert inspection duration time delta into seconds and divide by 60 for minutes

    relevant_closures_df = relevant_df[relevant_df['placard_st'] == 6]  # All relevant Pittsburgh closures
    relevant_df["zipstr"] = relevant_df["zip"].astype('int').astype('str')
    relevant_df["inspect_dur"] = relevant_df["inspect_dur"].astype('timedelta64[s]') / 60
    relevant_other_df = relevant_df[relevant_df['placard_st'] != 1]  # All relevant Pittsburgh statuses not permitted

    # Draw Plot for Each Category
    def inspectTimeScatter():
        #scatter plot with plot colors corresponding to placards
        plt.figure(figsize=(20, 12), dpi=80, facecolor='w', edgecolor='k')
        placcolors = [plt.cm.tab10(i / float(len(relevant_placs) - 1)) for i in range(len(relevant_placs))]

        for i, plac in enumerate(relevant_placs):
            plt.scatter('zipstr', 'inspect_dur',
                data=relevant_df.loc[relevant_df.placard_desc == plac, :],
                s=20, c=placcolors[i], label=str(plac))

        # Formatting
        plt.gca().set(xlim=(-1, 50), ylim=(1, 340),
                  xlabel='ZipCode', ylabel='Inspection Duration (mins)', )
        plt.xticks(rotation=45)

        plt.xticks(fontsize=12);
        plt.yticks(fontsize=12)
        plt.title("Scatterplot of Pittsburgh  Inspections by Zipcode", fontsize=22)
        plt.legend(fontsize=12)
        plt.show()

    # Count of all non-permitted inspections

    def nonPermittedGraph(relevant_other_df):

        relevant_other_df['placard_desc'].groupby([relevant_other_df.zipstr]).count().plot(kind='bar')
        plt.gca().set(xlim=(-1, 35), ylim=(0, 60),
                  xlabel='ZipCode', ylabel='Number of Non Permitted Inspections', )
        plt.xticks(rotation=45)

        plt.xticks(fontsize=12);
        plt.yticks(fontsize=12)
        plt.show()

    # Count of total inspections by zipcode
    def totalInspectByZipGraph(relevant_df):
        relevant_df['encounter'].groupby([relevant_df.zipstr]).count().plot(kind='bar')
        axs1 = plt.gca().set(xlim=(-1, 40), ylim=(0, 1400),
                         xlabel='ZipCode', ylabel='Number of Inspections', )
        plt.xticks(rotation=90)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.title("Scatterplot of Pittsburgh  Inspections by Zipcode", fontsize=22)
        plt.legend(fontsize=12)
        plt.show()


    # Grouped bar chart of total inspections and COVID inspections by zipcode
    # Use Address column created and facility name to ensure uniqueness and keep most recent inspection
    relevant_covid_df["zipstr"] = relevant_covid_df["zip"].astype('int').astype('str')
    unique_rel_covid_fnames = relevant_covid_df['Address'].unique().tolist()
    unique_rel_df = relevant_df.drop_duplicates(subset='Address', keep="last")
    unique_rel_covid_df = relevant_covid_df.drop_duplicates(subset='Address', keep="last")
    testlist = unique_rel_df['zipstr'].unique().tolist()

    # Count of total covid inspections by zipcode

    def inspectVsCovidGraph(unique_rel_def, unique_rel_covid_df, testlist ):
        unique_rel_df['encounter'].groupby([unique_rel_df.zipstr]).count().plot(kind='bar', label='regular inspection')
        cax = unique_rel_covid_df['encounter'].groupby([unique_rel_covid_df.zipstr]).count().plot(kind='bar', color='orange', label='covid inspection')
        plt.gca().set(xlim=(-1, 46), ylim=(0, 260),
                  xlabel='ZipCode', ylabel='Number of Inspections', )
        plt.xticks(range(0, len(testlist)), testlist)
        plt.title("Restaurant vs.COVID Inspections by Zipcode", fontsize=22)
        plt.xticks(rotation=80)
        plt.xticks(fontsize=12);
        plt.yticks(fontsize=12)
        plt.legend(fontsize=12)
        plt.show()

    # Now by Description
    def inspectTypeGraph(unique_rel_df):
        unique_rel_df['encounter'].groupby([unique_rel_df.description]).count().plot(kind='bar', color="purple", label='regular inspections')
        cax = unique_rel_covid_df['encounter'].groupby([unique_rel_covid_df.description]).count().plot(kind='bar',
                                                                                                   color='orange', label='covid inspections')
        desclist = unique_rel_df['description'].unique().tolist()
        plt.gca().set(xlim=(-1, 9), ylim=(0, 820),
                  xlabel='Restaurant Type', ylabel='Number of Inspections', )
        plt.xticks(range(0, len(desclist)), desclist)
        plt.title("Health/COVID Inspections by Facility Type", fontsize=22)
        plt.xticks(rotation=45)
        plt.xticks(fontsize=10);
        plt.yticks(fontsize=12)
        plt.legend(fontsize=12)
        plt.show()

    # Unique Restaurants complaints
    def whoIsComplainingGraph(unique_rel_df, testlist):
        purp_codes = [8, 54]
        unique_complaint_df = unique_rel_df.loc[unique_rel_df['ispt_purpose'].isin(purp_codes)]
        unique_rel_df['encounter'].groupby([unique_rel_df.zipstr]).count().plot(kind='bar', color="grey", label='regular inspections')
        com = unique_complaint_df['encounter'].groupby([unique_complaint_df.zipstr]).count().plot(kind='bar',
                                                                                              color='red', label='complaints')
        plt.gca().set(xlim=(-1, 45), ylim=(0, 280),
                  xlabel='ZipCode', ylabel='Number of Complaints and Inspections', )
        plt.xticks(range(0, len(testlist)), testlist)
        plt.title("Where are people complaining?", fontsize=22)
        plt.xticks(rotation=80)
        plt.xticks(fontsize=12);
        plt.yticks(fontsize=12)
        plt.legend(fontsize=12)
        plt.show()

        complain_df = relevant_df.loc[relevant_df['ispt_purpose'].isin(purp_codes)]
        complain_df["count"] = complain_df.groupby(['facility_name', 'Address'])['Address'].transform('count')
        hallofshame_df = complain_df.loc[complain_df['count'] >= 2]
        comp_max = hallofshame_df['count'].max()
        print("Max number of complaints: " + str(comp_max))
        print(hallofshame_df['facility_name'].loc[hallofshame_df['count'] == comp_max])


    inspectTypeGraph(unique_rel_df)
    inspectVsCovidGraph(unique_rel_df, unique_rel_covid_df, testlist)
    inspectTimeScatter()
    covidInspectTimeGraph(relevant_covid_df)
    whoIsComplainingGraph(unique_rel_df, testlist)


getStats()
