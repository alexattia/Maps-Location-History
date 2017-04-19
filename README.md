# Maps-Location-History
Get, Concatenate and Process you location history from Google Maps TimeLine

## Introduction
If you have turned on the Google Maps location history, you probably now that Google save your location data and process it in order to create a timeline that you can find in the user interface : https://www.google.fr/maps/timeline.  
Maps is using raw data (multiple points saved per minutes) and is projecting it on roads, places, etc.  
You can easily export all of the raw data saved by Maps or you can export one day to KML but it's impossible to export all of the processed data from the user interface.  
In this project, I export multiple days (months actually) to KML, then process it in order to convert it into a pandas DataFrame. I am still working on data vizualtion and statistics with this data.  

## Get cookie_content to export locatin history
In order to export processed data from Google Maps website from a python script, you need to get your actual cookie.
1. Go to https://www.google.fr/maps/timeline
2. Inspect the page and go to the Network tab
3. Enter this link https://www.google.fr/maps/timeline/kml?authuser=0&pb=!1m8!1m3!1i2017!2i3!3i16!2m3!1i2017!2i3!3i16 (or another date)
4. Save this element as a cURL
5. Open the cURL in a text editor

![Explanations Image](https://github.com/alexattia/Maps-Location-History/blob/master/saved_as_curl.png)

You should get something like this:
```
curl 'https://www.google.com/maps/timeline/kml?authuser=0&pb=!1m8!1m3!1i2017!2i3!3i16!2m3!1i2017!2i3!3i16'   
-H 'accept-encoding: gzip, deflate, sdch, br'   
-H 'accept-language: en-US,en;q=0.8,fr;q=0.6'   
-H 'upgrade-insecure-requests: 1'   
-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) '   
-H 'x-chrome-uma-enabled: 1'   
-H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' 
-H 'authority: www.google.com'   
-H '**cookie**: gsScrollPos=; _ga=GA1.1.49937635TxMcGmJ-uXXXXX gsScrollPos='  
-H 'x-client-data: XXXQ==' --compressed 
```
6. Save the cookie content

## Code explanations

1. Export and Save KML files
Choose a folder where you want to save the KML files.  
Pass the folder path, the cookie content and the days you want to save to the function :
`process_location.create_kml_files(begin_month, begin_day, end_month, end_day, cookie_content, folder)`

2. Create a dataframe
Pass the folder path where your files are saved to `df = process_location.full_df(folder)` to get a well formated dataframe.
