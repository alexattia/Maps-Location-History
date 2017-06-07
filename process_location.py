import pandas as pd
import requests
import calendar
import glob
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import numpy as np
from datetime import datetime
import imp
from mpl_toolkits.basemap import Basemap
from dateutil import tz

def convert_timezone(dtime):
    """
    Convert datetimes from UTC to localtime zone
    """
    utc_datetime = datetime.strptime(dtime, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_datetime = utc_datetime.replace(tzinfo=tz.tzutc())
    local_datetime = utc_datetime.astimezone(tz.tzlocal())
    return local_datetime.strftime("%Y-%m-%d %H:%M:%S")

def process(bs):
    """
    Convert KML file into a list of dictionnaries
    At this time, every place begin with Placemark tag in the KML file
    :param bs: beautiful soup object
    :return: list of places 
    """
    places = []
    for place in bs.find_all('Placemark'):
        dic = {}
        for elem in place:
            if  elem.name != 'Point':
                c = list(elem.children)
                e =  elem.find_all('Data')
                if len(c) == 1:
                    dic.update({elem.name.title(): ''.join(c)})
                elif len(e) > 1:
                    for d in e:
                        dic.update({d.attrs['name']: d.text})
                else:
                    dic.update({elem.name: [d.text for d in c]})
        places.append(dic)    
    return places

def create_places_list(json_file):
    """
    Open the KML. Read the KML. Process and create json.
    :param json_file: json file path
    :return: list of places
    """
    with open(json_file, 'r') as f:
        s = BeautifulSoup(f, 'xml')
    return process(s)

def convert_time(row):
    """
    Convert datimes into well-formated dates, get event duration
    """
    b_time = datetime.strptime(row['BeginTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
    e_time = datetime.strptime(row['EndTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
    delta = (e_time - b_time).total_seconds()
    m, s = map(int,divmod(delta, 60))
    h, m = divmod(m, 60)
    row['Duration'] = '%sh %smin %ssec' % (h, m, s)
    row['IndexTime'] = row['BeginTime'] = convert_timezone(row['BeginTime'])
    row['BeginDate'], row['BeginTime'] = row['BeginTime'].split(' ')
    row['EndDate'], row['EndTime'] = convert_timezone(row['EndTime']).split(' ')
    row['WeekDay'] = datetime.strptime(row['BeginDate'], "%Y-%m-%d").weekday()
    return row

def create_df(places):
    """
    Create a well formated pandas DataFrame
    One row is a event (place or moving)
    :param places: list of places
    :return: DataFrame
    """
    df = pd.DataFrame(places)
    times = df['TimeSpan'].apply(pd.Series).rename(columns={0:'BeginTime', 1:'EndTime'})
    df = pd.concat([df, times], axis = 1)
    df.drop(['TimeSpan', 'Email', 'Description'], axis=1, inplace=True)
    df['Track'] = df['Track'].apply(lambda x:[d.split(' ') for d in x if d != 'clampToGround'])
    df = df.apply(convert_time, axis=1)
    return df.sort_values('IndexTime', ascending=False)

def get_kml_file(month, day, cookie_content, folder):
    """
    Get KML file from your location history and save it in a chosen folder
    :param month: month of the location history
    :param day: day of the location history
    :param cookie_content: your cookie (see README)
    :param folder: path to the folder
    """
    cookies = dict(cookie=cookie_content)
    if type(month) == str:
        month = month[:3].title()
        cal = {v:k for k,v in enumerate(calendar.month_abbr, -1)}
        month_url = str(cal[month])
    else:
        month_url = str(int(month - 1))
    month_file = str(int(month_url) + 1)
    day_file = day_url = str(int(day))
    if len(month_file) == 1 :
        month_file = '0' + month_file
    if len(day_file) == 1 :
        day_file = '0' + day_file
    url = 'https://www.google.fr/maps/timeline/kml?authuser=0&pb=!1m8!1m3!1i2017!2i{0}!3i{1}!2m3!1i2017!2i{0}!3i{1}'.format(month_url, day_url)
    time.sleep(np.random.randint(0, 0.3))
    r = requests.get(url, cookies=cookies)
    if r.status_code == 200:
        with open(folder + 'history-2017-{}-{}.kml'.format(month_file, day_file), 'w') as f:
            f.write(r.text)
        
def create_kml_files(month_begin, day_begin, month_end, day_end, cookie_content, folder):
    """
    Create multiple KML files from a date range
    :param month_begin: first month of the location history
    :param day_begin: first day of the location history
    :param month_end: last month of the location history
    :param day_end: last day of the location history
    :param cookie_content: your cookie (see README)
    :param folder: path to the folder
    """
    months = list(calendar.month_abbr)
    month_range = [elem for elem in months if months.index(month_begin[:3].title()) <= months.index(elem) <= months.index(month_end[:3].title())]
    for month in month_range:
        for day in range(1, 32):
        #TODO get only chosen days
            get_kml_file(month, day, cookie_content, folder)
            
def full_df(folder):
    """
    Create a well formated DataFrame from multiple KML files
    :param folder: path to folder where are saved the KML files
    """
    df = pd.DataFrame()
    kml_files = glob.glob(folder + '*.kml')
    print('{0} KML files (ie {0} days) to concatenate'.format(len(kml_files)))
    for file in kml_files:
        df = pd.concat([df, create_df(create_places_list(file))])
    df = df.sort_values('IndexTime', ascending=False)
    # Need hashable elements to drop duplicates, tuples are, list aren't
    df = df[['Address', 'BeginDate', 'BeginTime', 'Category', 'Distance', 'Duration',
       'EndDate', 'EndTime', 'IndexTime', 'Name', 'Track', 'WeekDay']]
    for elem in df.columns:
        df[elem] = df[elem].apply(lambda x : tuple([tuple(p) for p in x]) if type(x) is list else x)
    df.drop_duplicates(inplace=True)
    df['Distance'] = df['Distance'].apply(int)
    return df.reset_index(drop=True)


def sec_to_time(sec):
    h, s = divmod(sec, 3600)
    m,s = divmod(s, 60)
    return h, m, s, "%02d:%02d:%02d" % (h,m,s)

