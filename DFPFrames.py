
import csv
import pandas as pd
import datetime
import itertools

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


    restaurant_df = pd.read_csv("PittsburghRestData.csv") # full restaurants file

    covid_df = restaurant_df.loc[restaurant_df['abrv'] == ('Covid-19' or 'Covid-19, Complaint')] # COVID dataframe
    pitt_df = restaurant_df.loc[restaurant_df['city'] == 'Pittsburgh']#All Pittsburgh dataframe
    pitt_df['inspect_dt'] = pd.to_datetime(pitt_df['inspect_dt'], format='%m/%d/%Y') # change inspect date from string to date time
    category_cd_list = [117, 118, 201, 202, 203, 211, 212, 250, 407] # relevant categeory codes
    cutoff = datetime.datetime(2018, 1, 1) #cutoff threshold for recency
    pitt_recent_df = pitt_df.loc[pitt_df['inspect_dt'] >= cutoff] #dataframe of recent inspections in Pittsburgh
    relevant_df = pitt_recent_df.loc[pitt_recent_df['category_cd'].isin(category_cd_list)] # dataframe fo recent inspection in Pittsburgh and of relevant categories
    pitt_covid_df = covid_df.loc[covid_df['city'] == 'Pittsburgh'] # Pittsburgh COVID dataframe
    relevant_covid_df = pitt_covid_df.loc[pitt_covid_df['category_cd'].isin(category_cd_list)] # COVID dataframe of restaurants with given categories and recency threshold
    relevant_closures_df = relevant_df[relevant_df['placard_st'] == 6] #All relevant Pittsburgh closures





    print(restaurant_df.columns)
    print(len(relevant_df))
    print(len(relevant_covid_df))
    print(len(relevant_closures_df))

    print(len(relevant_df['facility_name'].unique()))


    #Converts start_time and end_time fields from string to datetime
    #then creates a list of start times and a list of end times

    #All Pittsburgh food facilities COVID data
    pitt_covid_df['end_time'] = pd.to_datetime(pitt_covid_df['end_time'], format='%H:%M:%S')
    pitt_covid_df['start_time'] = pd.to_datetime(pitt_covid_df['start_time'], format='%H:%M:%S')

    #Chosen categories of  food facilities within Pittsburgh COVID data
    relevant_covid_df['end_time'] = pd.to_datetime(relevant_covid_df['end_time'], format='%H:%M:%S')
    relevant_covid_df['start_time'] = pd.to_datetime(relevant_covid_df['start_time'], format='%H:%M:%S')

    #All
    covid_start_times = pitt_covid_df['start_time'].tolist()
    covid_end_times = pitt_covid_df['end_time'].tolist()

    #Chosen
    rel_covid_start_times = relevant_covid_df['start_time'].tolist()
    rel_covid_end_times = relevant_covid_df['end_time'].tolist()





    #Creates  list for time differences between start and end, and initializes a count for all Pittsburgh and relevant categories
    covid_inspect_dur= []
    rel_covid_inspect_dur = []
    dirty_inspect_data = []
    rel_dirty_inspect_data = []
    count = 0




    #iterates through list of start times and finds difference between start and end times
    #disregards times that have a start time occurring after the end time:
    # 6/424 observations for all

    for t in covid_start_times:
        duration = covid_end_times[count]-t
        dirty_inspect_data.append(duration)
        if duration.total_seconds() >= 0:
            covid_inspect_dur.append(duration)
        count+=1

    count = 0

    for t in rel_covid_start_times:
        rduration = rel_covid_end_times[count] - t
        rel_dirty_inspect_data.append(rduration)
        if rduration.total_seconds() >= 0:
            rel_covid_inspect_dur.append(rduration)
        count += 1

    print(covid_inspect_dur)
    print(dirty_inspect_data)

    print(pitt_covid_df.columns)

    se = pd.Series(dirty_inspect_data)
    pitt_covid_df['inspect_dur'] = se.values

    sr = pd.Series(rel_dirty_inspect_data)
    relevant_covid_df['inspect_dur'] = sr.values


    #print(pitt_covid_df['inspect_dur'])

    pitt_df['inspect_dt'] = pd.to_datetime(pitt_df['inspect_dt'], format='%m/%d/%Y')

    print(pitt_df['inspect_dt'])

    #date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')

    pitt_df['inspect_dt']




    print(pitt_covid_df.columns)


    #initializes empty timedelta variable and sums the total time
    #then divides that total by the number of observations from cleaned data set

    total = datetime.timedelta(0)
    relevant_total = datetime.timedelta(0)

    for t in covid_inspect_dur:
        total = total + t

    for r in rel_covid_inspect_dur:
        relevant_total = relevant_total + r


    avg_covid_inspect_time = total/len(covid_inspect_dur)
    relevant_avg_covid_inspect_time = relevant_total / len(rel_covid_inspect_dur)
    num_covid_inspections = len(covid_inspect_dur)
    dead_data = len(covid_start_times) - len(covid_inspect_dur)
    init_obsv = len(covid_start_times)
    avg_covid_inspect_time = avg_covid_inspect_time - datetime.timedelta(microseconds=avg_covid_inspect_time.microseconds)
    relevant_avg_covid_inspect_time = relevant_avg_covid_inspect_time - datetime.timedelta(microseconds=relevant_avg_covid_inspect_time.microseconds)

    format_avg = str(avg_covid_inspect_time).split(".")[0].split(":")
    format_relevant = str(relevant_avg_covid_inspect_time).split(".")[0].split(":")

    print(len(pitt_df))

    print("Average time of COVID-19 Inspection: " + format_avg[1] + " minutes " + format_avg[2] + " seconds ")
    print("Average time of COVID-19 Inspections for Chosen Categories: " + format_relevant[1] + " minutes " + format_relevant[2] + " seconds ")
    print("Number of COVID-19 related visits by Health Department: " + str(init_obsv))
    print("Inspections included in average: " + str(num_covid_inspections))
    print("Faulty data removed from operation: " + str(dead_data))






       # = csv.DictReader(restaurantsCsv, delimiter=',')
    #headreader = csv.reader(restaurantsCsv, delimiter=',')

    #header = str(next(headreader)).split(',')
    #header = next(headreader)
    covidDict = {}
    #print(header)
    #print(formatheader)
    #print(reader)
    #for row in reader:
        #if row['purpose'] == "COVID-19":
            #print(row)
        #print(row['facility_name'])



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


