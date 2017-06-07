import pandas as pd
import numpy as np
import time
import re
import numpy as np
from datetime import datetime
from mpl_toolkits.basemap import Basemap

def get_sec(time_str):
    """
    Convert time string to seconds
    """
    h,m,s = re.sub("[^0-9]", " ",time_str).split()
    return int(h) * 3600 + int(m) * 60 + int(s)

def time_at(df, address=None, name=None, category=None):
    """
    Process dataframe for getting time stats about an activity or place
    :param address: place address
    :param name: place name
    :param category: activity (driving, walking ...)
    :return: dataframe with rows doing or beeing, total hours at, number of days of timelapse, activity/place
    """
    delta = datetime.strptime(df['EndDate'].max(), "%Y-%m-%d") - datetime.strptime(df['BeginDate'].min(), "%Y-%m-%d")
    delta = delta.days
    if address:
        df2 = df[df['Address'] == address]
        at = address
    elif name:
        df2 = df[df['Name'] == name]
        at = name
    elif category:
        df2 = df[df['Category'] == category.title()]
        at = category
    df2.loc[:,'DurationMin'] = df2.loc[:,'Duration'].apply(get_sec) / 60
    total_min = df2['DurationMin'].sum()
    total_hours = total_min / 60
    return df2, total_hours, delta, at

def time_at_doing(df, category):
    """
    Get time stats doing an activity
    :param category: activity (driving, walking ...)
    :return: dataframe with rows beeing doing this activity
    """
    df2, total_hours, delta, at = time_at(df, category=category)
    mean_min = round(df2['DurationMin'].mean(), 1)
    mean_dist = round(df2['Distance'].mean()*0.001, 1)
    n_times_per_day = len(df2) / len(df2['BeginDate'].unique())
    act_dist_tot = df2['Distance'].sum()*0.001
    act_dist_per_day = act_dist_tot / len(df2['BeginDate'].unique())
    try:
        print("For {} days, I have been {} {} times/day : {} km in total ({} km/days).".format(
                delta, at, round(n_times_per_day,1), round(act_dist_tot, 1), round(act_dist_per_day, 1)))
        print("On average, each time I am {} is for {} min and {} km.".format(
                at, mean_min, mean_dist))
        return df2.reset_index(drop=True)
    except ZeroDivisionError:
        print('You never did this activity!')

def time_at_place(df, address=None, name=None):
    """
    Get time stats at a specific place
    :param address: place address
    :param name: place name
    :return: dataframe with rows beeing at this place
    """
    df2, total_hours, delta, at = time_at(df, address=address, name=name, category=None)
    total_day_address = len(df2['BeginDate'].unique())
    try:
        print("For {} days, I have been {} times at {} for a total of {} hours or {} hours/day".format(
                delta, total_day_address, at, round(total_hours, 1), round(total_hours/total_day_address, 1)))
        return df2.reset_index(drop=True)
    except ZeroDivisionError:
        print('You never been to this place')

def get_dict_doing(df_doing):
    """
    Get time, distance, speed while doing an activity (e.g driving) for every day.
    :param: dataframe with rows beeing doing this activity
    :return: dictionnary of dictionnary {date:value} for time, distance, speed doing this
    """
    types = ['time','dist','speed']
    means = {t:[] for t in types}
    dicts = {t:{} for t in types}
    for day in sorted(df_doing['BeginDate'].unique()):
        a = df_doing[df_doing['BeginDate'] == day].DurationMin.sum()
        b = df_doing[df_doing['BeginDate'] == day].Distance.sum()*0.001
        dicts['time'].update({day:a})
        dicts['dist'].update({day:b})
        dicts['speed'].update({day: b/(a/60)})
    return dicts

def plot_basemap(dataframe=None, borders=None, ax=None, title=None):
    """
    Plot on a basemap with passed limits scatter points
    :param dataframe: dataframe containing all wanted points to plot
    :param borders: llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat
    :param ax: for matplotlib subplot
    :param title: plot title
    """
    longitudeArray = [float(elem[0]) for elem in np.concatenate(list(dataframe.Track))]
    latitudeArray = [float(elem[1]) for elem in np.concatenate(list(dataframe.Track))]
    if borders:
        (llcrnrlon_sf, llcrnrlat_sf, urcrnrlon_sf, urcrnrlat_sf) = borders
    else:
        llcrnrlon_sf = min(longitudeArray) 
        llcrnrlat_sf = min(latitudeArray)
        urcrnrlon_sf = max(longitudeArray)
        urcrnrlat_sf = max(latitudeArray)
    m = Basemap(llcrnrlon=llcrnrlon_sf, #Set map's displayed max/min based on your set's max/min
        llcrnrlat=llcrnrlat_sf,
        urcrnrlon=urcrnrlon_sf,
        urcrnrlat=urcrnrlat_sf,
        lat_ts=20, #"latitude of true scale" lat_ts=0 is stereographic projection
        resolution='h', #resolution can be set to 'c','l','i','h', or 'f' - for crude, low, intermediate, high, or full
        projection='merc',
        lon_0=longitudeArray[0],
        lat_0=latitudeArray[0], ax = ax)
    x1, y1 = m(longitudeArray, latitudeArray) #map the lat, long arrays to x, y coordinate pairs
    m.drawmapboundary(fill_color="white", ax = ax)
    m.drawcoastlines(ax = ax)
    m.drawcountries(ax = ax)
    m.scatter(x1, y1, s=25, c='r', marker="o", ax=ax) #Plot your markers and pick their size, color, and shape
    if title:
        ax.set_title(title)