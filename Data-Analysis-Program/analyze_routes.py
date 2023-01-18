import json
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
import numpy as np
import math
import re


def log(question, output_df, other):
    print("--------------- {}----------------".format(question))

    if other is not None:
        print(question, other)
    if output_df is not None:
        df = output_df.head(5).copy(True)
        for c in df.columns:
            df[c] = df[c].apply(lambda a: a[:20] if isinstance(a, str) else a)

        df.columns = [a[:10] + "..." for a in df.columns]
        print(df.to_string())
        

def get_unknown(row):
    if row['service_direction_name'] == 'Unknown':
        row['service_direction_name'] = row['route_search_name']
    return row

        
def clean_service_direction_name(route):
    first_via = route.find(' via ')
    if first_via > -1:
        route = route[:first_via] 
    
    bracket_start = route.find('(')
    bracket_end = route.find(')')
    if bracket_start > -1 and bracket_end > -1:
        route = route[:bracket_start] + route[bracket_end+1:]
        
    route = route.replace(' loop', '')
    route = route.replace(' and return', '')
    route = route.replace(' and rtn', '')
    return route

def add_start(route):
    if ',' in route:
        if ' then ' in route and ' to ' in route:
            route = route.split(',')[0]
            if ' all ' in route:
                route = route.split(' ')[0]
        elif ' then ' in route:
            route = route.replace(' then ', '')
            route = route.split(',')[0]
        elif ' to ' in route:
            route = route.split(' to ')[0]
            if route.count(',') > 1:
                route = route.split(',')[0]
        else:
            route = route.split(',')[0]
    elif ' to ' in route:
        route = route.split(' to ')[0]
        if ' and ' in route:
            route = route.split(' and ')[0]
        if ' or ' in route:
            route = route.split(' or ')[0]
        if '-' in route:
            str1 = route.split('-')[0]
            if 'Bus ' in str1 or 'Town ' in str1 or 'RBCC ' in str1 or 'Uralla ' in str1 or 'Koala ' in str1:
                route = route.split('-')[1]  
    elif '-' in route:
        if 'RBCC' in route.split('-')[0]:
            route = route.split('-')[1]
        else:
            route = route.split('-')[0]
    else:
        route = 'Unknown'
    return route.strip()

def add_end(route):
    if ',' in route:
        if ' then ' in route and ' to ' in route:
            route = route.replace(' then all stations to ', ',')
            route = route.replace('all to ', ',')
            route = route.replace('then ', ',')
            route = route.replace('stations ', ',')
            route = route.split(',')[-1]
        elif ' then ' in route:
            route = route.replace(' then ', '')
            route = route.split(',')[-1]
        elif ' to ' in route:
            route = route.split(' to ')[-1]
            if route.count(',') > 1:
                route = route.split(',')[-1]
        else:
            route = route.split(',')[-1]
            route = route.replace(' and ', '')
    elif ' to ' in route:
        route = route.split(' to ')[-1]
        if ' and ' in route:
            route = route.split(' and ')[-1]
        if ' or ' in route:
            route = route.split(' or ')[-1]
    elif '-' in route:
        route = route.split('-')[-1]
    else:
        route = 'Unknown'
    return route.strip()


def final_cleaning(row):
    while('  ' in row['start']):
        row['start'] = row['start'].replace('  ', ' ')
    while('  ' in row['end']):
        row['end'] = row['end'].replace('  ', ' ')        
    
    if ' Loop' in row['end']:
        row['end'] = row['end'].replace(' Loop', '')
        
        
    if row['start'] == 'Cen':
        row['start'] = 'Central'
    if row['end'] == 'Cen':
        row['end'] = 'Central'
        
    if row['start'] == 'Nwcstl':
        row['start'] = 'Newcastle'
    if row['end'] == 'Nwcstl':
        row['end'] = 'Newcastle'
        
    if row['start'] == 'Broken Hill Town':
        row['start'] = 'Broken Hill'
    if row['end'] == 'Broken Hill Town':
        row['end'] = 'Broken Hill'
        
    if row['start'] == 'Dangar':
        row['start'] = 'Dangar Island'
    if row['end'] == 'Dangar':
        row['end'] = 'Dangar Island'
        
    if row['start'] == 'Olympic Park':
        row['start'] = 'Sydney Olympic Park'
    if row['end'] == 'Olympic Park':
        row['end'] = 'Sydney Olympic Park'
        
    if row['start'] == 'Mosman Bay':
        row['start'] = 'Mosman'
    if row['end'] == 'Mosman Bay':
        row['end'] = 'Mosman'
        
    if row['start'] == 'Queanbeyan Bus Interchange':
        row['start'] = 'Queanbeyan'
    if row['end'] == 'Queanbeyan Bus Interchange':
        row['end'] = 'Queanbeyan'
        
    if row['start'] == 'Pyrmont Bay':
        row['start'] = 'Pyrmont'
    if row['end'] == 'Pyrmont Bay':
        row['end'] = 'Pyrmont'        
        
    return row

def question_1(routes, suburbs):
    """
    :param routes: the path for the routes dataset
    :param suburbs: the path for the routes suburbs
    :return: df1
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    
    df = pd.read_csv(routes)
    
    df = df.apply(get_unknown, axis = 1)
    df["service_direction_name"] = df["service_direction_name"].apply(clean_service_direction_name)
    
    df1 = df.assign(start=df["service_direction_name"], end=df["service_direction_name"])
    
    df1["start"] = df1["start"].apply(add_start)
    df1["end"] = df1["end"].apply(add_end)
    
    df1[['start', 'end']] = df1[['start', 'end']].apply(final_cleaning, axis = 1)

    
    #################################################

    log("QUESTION 1", output_df=df1[["service_direction_name", "start", "end"]], other=df1.shape)
    return df1


def question_2(df1):
    """
    :param df1: the dataframe created in question 1
    :return: dataframe df2
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    
    start = df1[["start"]].rename(columns={'start': 'service_location'})
    end = df1[["end"]].rename(columns={'end': 'service_location'})
    
    all_stops = pd.concat([start, end], axis=0, ignore_index= True)
    all_stops = all_stops[all_stops['service_location'] != 'Unknown']
    
    df2 = all_stops.groupby('service_location')['service_location'].count().reset_index(name = 'frequency')    
    df2 = df2.sort_values(by= ['frequency'], ascending= False)
    
    df2 = df2.head()
    #################################################

    log("QUESTION 2", output_df=df2, other=df2.shape)
    return df2


def map_names(transport_name):
    if 'bus' in transport_name.lower():
        return 'Bus'
    elif 'ferr' in transport_name.lower():
        return 'Ferry'
    elif 'light rail' in transport_name.lower():
        return 'Light Rail'
    elif 'train' in transport_name.lower():
        return 'Train'
    elif 'metro' in transport_name.lower():
        return 'Metro'
    else:
        return 'Bus'


def question_3(df1):
    """
    :param df1: the dataframe created in question 1
    :return: df3
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """
    #################################################
    # Your code goes here ...
    df3 = df1
    df3["transport_name"] = df3["transport_name"].apply(map_names)
    
    #################################################

    log("QUESTION 3", output_df=df3[['transport_name']], other=df3.shape)
    return df3


def question_4(df3):
    """
    :param df3: the dataframe created in question 3
    :param continents: the path for the Countries-Continents.csv file
    :return: df4
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    transport_name = df3[["transport_name"]]    
    
    df4 = transport_name.groupby('transport_name')['transport_name'].count().reset_index(name= 'frequency')
    df4 = df4.sort_values(by=["frequency"])
    
    df4 = df4.head()
    #################################################

    log("QUESTION 4", output_df=df4[["transport_name", "frequency"]], other=df4.shape)
    return df4


def clean_depot_names(depot):
    depot = depot.split(', ')[-1]
    if depot == 'Mt Kuring gai':
        depot = 'Mount Kuring-Gai'
    return depot

def filter_out_suburb(dfs):
    if dfs['state'] != 'NSW':
        dfs['state'] = np.NaN
    if dfs['population'] == 0:
        dfs['state'] = np.NaN
    if dfs['depot'] == 'Punchbowl' and dfs['population'] == 3:
        dfs['state'] = np.NaN
    return dfs

def get_ratio(dfs):
    return dfs['frequency'] / dfs['population']

def question_5(df3, suburbs):
    """
    :param df3: the dataframe created in question 2
    :param suburbs : the path to dataset
    :return: df5
            Data Type: dataframe
            Please read the assignment specs to know how to create the output dataframe
    """
    #################################################
    # Your code goes here ...
    
    sub_population = pd.read_csv(suburbs)[['suburb', 'state', 'population']]
    sub_population = sub_population.rename(columns={'suburb': 'depot'})
    
    depot = df3[["depot_name"]]   
    depot = depot.rename(columns={'depot_name': 'depot'}) 
    depot = depot.dropna()        
    depot['depot'] = depot['depot'].apply(clean_depot_names)       
    depot_frequency = depot.groupby('depot')['depot'].count().reset_index(name= 'frequency')
    
    df5 = pd.merge(depot_frequency, sub_population, on='depot', how = 'inner')    
    df5 = df5.apply(filter_out_suburb, axis = 1)
    df5 = df5.dropna()    
    
    df5['ratio'] = df5.apply(get_ratio, axis = 1)    
    df5 = df5.drop(columns = ['frequency', 'state', 'population'])
    df5 = df5.sort_values(by = ['ratio'], ascending = False)
    df5 = df5.head()
    df5 = df5.set_index('depot', inplace = False)
    
    
    #################################################

    log("QUESTION 5", output_df=df5[["ratio"]], other=df5.shape)
    return df5


def question_6(df3):
    """
    :param df3: the dataframe created in question 3
    :return: nothing, but saves the figure on the disk
    """
    table = None
    #################################################
    # Your code goes here ...
    
    counts = df3[['operator_name', 'transport_name']]    
    counts = counts.groupby(['operator_name', 'transport_name'])['transport_name'].count().reset_index(name="NUMBER OF ROUTES")    
    counts = counts.sort_values(by=['NUMBER OF ROUTES'], ascending= False)  
    counts = counts.rename(columns={'operator_name':'OPERATOR NAME', 'transport_name': 'TRANSPORT METHOD'})
    
   
    table = counts.pivot_table(index = ['OPERATOR NAME'], columns = 'TRANSPORT METHOD', fill_value = 0, sort=False)    
    
    #################################################

    log("QUESTION 6", output_df=None, other=table)
    return table


def remove_brackets(LGA):
    bracket_start = LGA.find('(')
    bracket_end = LGA.find(')')
    LGA = LGA[:bracket_start] + LGA[bracket_end+1:]
    return LGA


def question_7(df3,suburbs):
    """
    :param df3: the dataframe created in question 3
    :param suburbs : the path to dataset
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    # Your code goes here ...
    
    suburb = pd.read_csv(suburbs)
    LGAs = suburb[['local_goverment_area', 'population', 'median_income', 'sqkm']]    
    LGAs = LGAs[suburb['statistic_area'] == 'Greater Sydney']
    LGAs = LGAs.sort_values(by= ['local_goverment_area', 'median_income'])  
    
    population = LGAs.groupby('local_goverment_area')['population'].sum().reset_index(name= 'population')    
    sqkm = LGAs.groupby('local_goverment_area')['sqkm'].sum().reset_index(name= 'sqkm')       
    df7 = pd.merge(population, sqkm, on= 'local_goverment_area', how= 'inner')    
    
    total_pop = pd.merge(LGAs, population, left_on= 'local_goverment_area', right_on= 'local_goverment_area')    
    total_pop['total'] = (total_pop['population_x'] * total_pop['median_income']) / total_pop['population_y']    
    median = total_pop.groupby('local_goverment_area')['total'].sum().reset_index(name= 'median_income')    
    df7 = pd.merge(df7, median, on= 'local_goverment_area', how= 'inner')    
    
    df7['pop_per_sqkm'] = df7['population'] / df7['sqkm']
    df7['income_per_sqkm'] = df7['median_income'] / df7['sqkm']    
    df7['local_goverment_area'] = df7['local_goverment_area'].apply(remove_brackets)
    
    df7 = df7[df7['population'] != 0]
    df7 = df7.sort_values(by= ['population'])
    

    plt.figure(figsize=(40, 13.5))
    
    plt.subplot(131)
    plt.xlabel('Population')
    plt.ylabel('NSW LGAs under Greater Sydney area')  
    plt.title('LGAs vs Population')
    plt.barh(df7['local_goverment_area'], df7['population'])
    
    
    plt.subplot(132)    
    
    plt.xlabel('Population per Area(sqkm)')  
    plt.title('LGAs vs Population per Sqkm Area')
    plt.barh(df7['local_goverment_area'], df7['pop_per_sqkm'])
    
    
    plt.subplot(133)
    
    
    plt.xlabel('Median Income')  
    plt.title('LGAs vs Median Income')
    plt.barh(df7['local_goverment_area'], df7['median_income'])
        
    
    plt.suptitle('Graphs Showing Relationship Between Population, Population Density and Median Income for NSW LGAs under Greater Sydney Area') 
    
    
    #################################################

    plt.savefig("{}-Q7.png".format(755817))


def remove_routes(row):
    if row['transport_name'] == 'Bus':
        row['start'] = np.NaN
    if row['start'] == 'Unknown' or row['end'] == 'Unknown':
        row['start'] = np.NaN
    return row


def matching_to_suburb(row):
        
    if row['start'] == 'Tallawong':
        row['start'] = 'Rouse Hill'
    if row['end'] == 'Tallawong':
        row['end'] = 'Rouse Hill'
        
    if row['start'] == 'Newcastle Interchange':
        row['start'] = 'Wickham'
    if row['end'] == 'Newcastle Interchange':
        row['end'] = 'Wickham'
        
    if row['start'] == 'Newcastle Beach':
        row['start'] = 'Newcastle'
    if row['end'] == 'Newcastle Beach':
        row['end'] = 'Newcastle'
        
    if row['start'] == 'Circular Quay':
        row['start'] = 'Sydney'
    if row['end'] == 'Circular Quay':
        row['end'] = 'Sydney'
        
    if row['start'] == 'City':
        row['start'] = 'Sydney'
    if row['end'] == 'City':
        row['end'] = 'Sydney'
        
    if row['start'] == 'Central':
        row['start'] = 'Haymarket'
    if row['end'] == 'Central':
        row['end'] = 'Haymarket'
        
    if row['start'] == 'Juniors Kingsford':
        row['start'] = 'Kingsford'
    if row['end'] == 'Juniors Kingsford':
        row['end'] = 'Kingsford'
        
    if row['start'] == 'Broken Hill':
        row['start'] = np.NaN
    if row['end'] == 'Broken Hill':
        row['end'] = np.NaN
        
    if row['start'] == 'Palm Beach':
        row['start'] = np.NaN
    if row['end'] == 'Palm Beach':
        row['end'] = np.NaN
        
    return row


def get_marker(area):
    if area < 1:
        return 'x'  
    if area >= 1 and area < 5:
        return 's'  
    if area >= 5 and area < 15:
        return 'o'  
    if area >= 15:
        return 'd' 

def get_label(area):
    if area < 1:
        return '< 1 sqkm'  
    if area >= 1 and area < 5:
        return '1-5 sqkm'  
    if area >= 5 and area < 15:
        return '5-15 sqkm'  
    if area >= 15:
        return '>= 15 sqkm'  
    

def fix_text_alignment(row):
    if (row['suburb_x'] == 'Leppington'):
        row['lng_x'] = row['lng_x'] + 0.004
        row['lat_x'] = row['lat_x'] - 0.07
        
    if (row['suburb_x'] == 'Church Point'):
        row['lng_x'] = row['lng_x'] + 0.015
        row['lat_x'] = row['lat_x'] - 0.02
        
    if (row['suburb_x'] == 'Elvina Bay'):
        row['lng_x'] = row['lng_x'] - 0.008
        row['lat_x'] = row['lat_x'] - 0.02
        
    if (row['suburb_x'] == 'Bundeena'):
        row['lng_x'] = row['lng_x'] - 0.01
        row['lat_x'] = row['lat_x'] - 0.02
        
    if (row['suburb_x'] == 'Lidcombe'):
        row['lat_x'] = row['lat_x'] - 0.06
        
    if (row['suburb_x'] == 'Kingsford'):
        row['lat_x'] = row['lat_x'] - 0.06
        
    if (row['suburb_x'] == 'Randwick'):
        row['lat_x'] = row['lat_x'] - 0.06
        row['lng_x'] = row['lng_x'] + 0.007
        
    if (row['suburb_x'] == 'Bondi Junction'):
        row['lat_x'] = row['lat_x'] - 0.05
        row['lng_x'] = row['lng_x'] + 0.01
        
    if (row['suburb_x'] == 'Watsons Bay'):
        row['lat_x'] = row['lat_x'] - 0.075
        row['lng_x'] = row['lng_x'] + 0.005
        
    if (row['suburb_x'] == 'Haymarket'):
        row['lat_x'] = row['lat_x'] - 0.07
        row['lng_x'] = row['lng_x'] + 0.005
        
    if (row['suburb_x'] == 'Pyrmont'):
        row['lat_x'] = row['lat_x'] - 0.025
        row['lng_x'] = row['lng_x'] - 0.01
        
    if (row['suburb_x'] == 'Sydney'):
        row['lat_x'] = row['lat_x'] + 0.003
        row['lng_x'] = row['lng_x'] - 0.003
        
    if (row['suburb_x'] == 'Dangar Island'):
        row['lat_x'] = row['lat_x'] - 0.04
        row['lng_x'] = row['lng_x'] + 0.012
        
    if (row['suburb_x'] == 'Brooklyn'):
        row['lat_x'] = row['lat_x'] - 0.03
        row['lng_x'] = row['lng_x'] - 0.012
        
    if (row['suburb_x'] == 'Woy Woy'):
        row['lat_x'] = row['lat_x'] - 0.025
        row['lng_x'] = row['lng_x'] - 0.01
        
    if (row['suburb_x'] == 'Empire Bay'):
        row['lat_x'] = row['lat_x'] - 0.035
        row['lng_x'] = row['lng_x'] + 0.015
        
    if (row['suburb_x'] == 'Dulwich Hill'):
        row['lat_x'] = row['lat_x'] - 0.075
        
    if (row['suburb_x'] == 'Mosman'):
        row['lng_x'] = row['lng_x'] + 0.005
        
    return row

def fix_transport_alignment(row):    
        
    if (row['my_timetable_route_name'] == 'BUNC'):
        row['mid_lat'] = row['mid_lat'] - 0.01
        row['mid_lng'] = row['mid_lng'] + 0.008
        
    if (row['my_timetable_route_name'] == 'MWB'):
        row['mid_lat'] = row['mid_lat'] - 0.01
        row['mid_lng'] = row['mid_lng'] + 0.008
        
    if (row['my_timetable_route_name'] == 'CHCP'):
        row['mid_lat'] = row['mid_lat'] + 0.01
        
    if (row['my_timetable_route_name'] == 'EMPB'):
        row['mid_lat'] = row['mid_lat'] - 0.03
        
    if (row['my_timetable_route_name'] == 'BRKL'):
        row['mid_lat'] = row['mid_lat'] + 0.001
        row['mid_lng'] = row['mid_lng'] - 0.01
        
    if (row['my_timetable_route_name'] == 'CCWM'):
        row['mid_lat'] = row['mid_lat'] + 0.025
        row['mid_lng'] = row['mid_lng'] + 0.015
        
    if (row['my_timetable_route_name'] == 'CCWB'):
        row['mid_lat'] = row['mid_lat'] - 0.003
        row['mid_lng'] = row['mid_lng'] + 0.02
        
    if (row['my_timetable_route_name'] == 'T1'):
        row['mid_lng'] = row['mid_lng'] + 0.007
        
    if (row['my_timetable_route_name'] == 'T7'):
        row['mid_lng'] = row['mid_lng'] - 0.01
        
    if (row['my_timetable_route_name'] == 'L1'):
        row['mid_lat'] = row['mid_lat'] - 0.015
        
    if (row['my_timetable_route_name'] == 'L2'):
        row['mid_lng'] = row['mid_lng'] + 0.005
        
    if (row['my_timetable_route_name'] == 'L3'):
        row['mid_lat'] = row['mid_lat'] - 0.015
        row['mid_lng'] = row['mid_lng'] - 0.008
        
    if (row['my_timetable_route_name'] == 'F6'):
        row['mid_lat'] = row['mid_lat'] + 0.02
        
    if (row['my_timetable_route_name'] == 'T4'):
        row['mid_lng'] = row['mid_lng'] - 0.008
        
    if (row['my_timetable_route_name'] == 'T2'):
        row['mid_lat'] = row['mid_lat'] - 0.015
        
    if (row['my_timetable_route_name'] == 'T5'):
        row['mid_lng'] = row['mid_lng'] + 0.008
        
    if (row['my_timetable_route_name'] == 'F3'):
        row['mid_lat'] = row['mid_lat'] + 0.005
        
    if (row['my_timetable_route_name'] == 'F5'):
        row['mid_lng'] = row['mid_lng'] + 0.005
        
    if (row['my_timetable_route_name'] == 'M'):
        row['mid_lat'] = row['mid_lat'] + 0.005
        
    if (row['my_timetable_route_name'] == 'T2' and row['mid_lat'] > -33.9):
        row['mid_lat'] = np.NaN
        
    if (row['my_timetable_route_name'] == 'F9' or row['my_timetable_route_name'] == 'F1' or row['my_timetable_route_name'] == 'MFF'):
        row['mid_lat'] = np.NaN
        
    return row


def question_8(df3,suburbs):
    """
    :param df3: the dataframe created in question 3
    :param suburbs : the path to dataset
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    # Your code goes here ...
    
    suburb = pd.read_csv(suburbs)[['suburb', 'state', 'lat', 'lng', 'sqkm']]
    suburb = suburb[suburb['state'] == 'NSW']
    
    # for showing routes only for main areas with most data
    suburb = suburb[suburb['lat'] > -34.2]
    suburb = suburb[suburb['lat'] < -33.2]
    suburb = suburb[suburb['lng'] > 150.7] # 150.85
    suburb = suburb[suburb['lng'] < 152]
    
    
    suburb_routes = df3[['start', 'end', 'transport_name', 'my_timetable_route_name', 'efa_route_name']]
    
    suburb_routes = suburb_routes.apply(remove_routes, axis= 1)
    suburb_routes = suburb_routes.apply(matching_to_suburb, axis= 1)
    suburb_routes = suburb_routes.dropna()
    
    
    matched_routes = pd.merge(suburb_routes, suburb, left_on= 'start', right_on= 'suburb', how= 'left')
    matched_routes = pd.merge(matched_routes, suburb, left_on= 'end', right_on= 'suburb', how= 'left')
    matched_routes = matched_routes.dropna()
    
    
    points_start = matched_routes.copy(True)
    points_start = points_start[['suburb_x', 'lat_x', 'lng_x', 'sqkm_x']]
    
    points_end = matched_routes.copy(True)
    points_end = points_end[['suburb_y','lat_y', 'lng_y', 'sqkm_y']]
    points_end = points_end.rename(columns= {'suburb_y': 'suburb_x','lat_y': 'lat_x', 'lng_y':'lng_x', 'sqkm_y': 'sqkm_x'})
    

    all_points = pd.concat([points_start, points_end], axis=0, ignore_index=True)
    all_points = all_points.drop_duplicates()
    
    
    plt.figure(figsize=(12, 12))
    
    plt.xlabel('Latitude of suburbs')
    plt.ylabel('Longitude of suburbs')
    plt.title('Map of different routes between main NSW LGAs showing transport types and suburb areas')
    
    # plotting lines for routes 
    color_map = {'Light Rail':'Red', 'Train':'Orange', 'Ferry':'Green', 'Metro': 'Blue'}
    matched_routes.apply(lambda row: plt.plot([row['lat_x'], row['lat_y']], [row['lng_x'], row['lng_y']], color= color_map[row['transport_name']], zorder=1), axis = 1)
    
    # just for printing UNIQUE labels for transport type
    train_routes = matched_routes[matched_routes['transport_name'] == 'Train'].head(1)
    ferry_routes = matched_routes[matched_routes['transport_name'] == 'Ferry'].head(1)
    metro_routes = matched_routes[matched_routes['transport_name'] == 'Metro'].head(1)
    light_rail_routes = matched_routes[matched_routes['transport_name'] == 'Light Rail'].head(1)
    train_routes.apply(lambda row: plt.plot([row['lat_x'], row['lat_y']], [row['lng_x'], row['lng_y']], label=row['transport_name'], color= color_map[row['transport_name']], zorder=1), axis = 1)
    ferry_routes.apply(lambda row: plt.plot([row['lat_x'], row['lat_y']], [row['lng_x'], row['lng_y']], label=row['transport_name'], color= color_map[row['transport_name']], zorder=1), axis = 1)
    metro_routes.apply(lambda row: plt.plot([row['lat_x'], row['lat_y']], [row['lng_x'], row['lng_y']], label=row['transport_name'], color= color_map[row['transport_name']], zorder=1), axis = 1)
    light_rail_routes.apply(lambda row: plt.plot([row['lat_x'], row['lat_y']], [row['lng_x'], row['lng_y']], label=row['transport_name'], color= color_map[row['transport_name']], zorder=1), axis = 1)
    
    
    # just for printing UNIQUE labels for area
    area_1 = matched_routes[matched_routes['sqkm_x'] < 1].head(1)
    area_1_5 = matched_routes[matched_routes['sqkm_x'] >= 1]
    area_1_5 = area_1_5[area_1_5['sqkm_x'] < 5].head(1)
    area_5_15 = matched_routes[matched_routes['sqkm_x'] > 5]
    area_5_15 = area_5_15[area_5_15['sqkm_x'] < 15].head(1)
    area_15 = matched_routes[matched_routes['sqkm_x'] > 15].head(1)
    
    area_1.apply(lambda row: plt.scatter(row['lat_x'], row['lng_x'], s=30, marker=get_marker(row['sqkm_x']), c='black', label=get_label(row['sqkm_x']), zorder=2), axis = 1)
    area_1_5.apply(lambda row: plt.scatter(row['lat_x'], row['lng_x'], s=30, marker=get_marker(row['sqkm_x']), c='black', label=get_label(row['sqkm_x']), zorder=2), axis = 1)
    area_5_15.apply(lambda row: plt.scatter(row['lat_x'], row['lng_x'], s=30, marker=get_marker(row['sqkm_x']), c='black', label=get_label(row['sqkm_x']), zorder=2), axis = 1)
    area_15.apply(lambda row: plt.scatter(row['lat_x'], row['lng_x'], s=30, marker=get_marker(row['sqkm_x']), c='black', label=get_label(row['sqkm_x']), zorder=2), axis = 1)
    
    # for printing suburb points and names
    all_points.apply(lambda row: plt.scatter(row['lat_x'], row['lng_x'], s=30, marker=get_marker(row['sqkm_x']), c='black', zorder=2), axis = 1)
    
    all_points['lat_x'] = all_points['lat_x'] + 0.006
    all_points['lng_x'] = all_points['lng_x'] - 0.005
    all_points = all_points.apply(fix_text_alignment, axis=1)
    all_points.apply(lambda row: plt.text(row['lat_x'], row['lng_x'], row['suburb_x']), axis = 1)
        
    
    # for printing transport names
    matched_routes['mid_lat'] = (matched_routes['lat_x'] + matched_routes['lat_y']) / 2
    matched_routes['mid_lng'] = (matched_routes['lng_x'] + matched_routes['lng_y']) / 2
    
    matched_routes = matched_routes[['transport_name', 'my_timetable_route_name', 'mid_lat', 'mid_lng']]
    matched_routes = matched_routes.drop_duplicates()
    
    matched_routes = matched_routes.apply(fix_transport_alignment, axis=1)
    matched_routes = matched_routes.dropna()
    matched_routes.apply(lambda row: plt.text(row['mid_lat'], row['mid_lng'], row['my_timetable_route_name'], color= color_map[row['transport_name']]), axis = 1)
    
    plt.legend()
    
    #################################################   
    

    plt.savefig("{}-Q8.png".format(755817))



if __name__ == "__main__":
    df1 = question_1("routes.csv", "suburbs.csv")
    df2 = question_2(df1.copy(True))
    df3 = question_3(df1.copy(True))
    df4 = question_4(df3.copy(True))
    df5 = question_5(df3.copy(True), "suburbs.csv")
    table = question_6(df3.copy(True))
    question_7(df3.copy(True), "suburbs.csv")
    question_8(df3.copy(True), "suburbs.csv")