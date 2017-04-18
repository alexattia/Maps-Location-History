# Maps-Location-History
Get, Concatenate and Process you location history from Google Maps TimeLine

Go to https://www.google.fr/maps/timeline
click on “Today”
Export this day to KML
Back to Chrome, go to Downloads, save link (https://www.google.fr/maps/timeline/kml?authuser=0&pb=!1m8!1m3!1i2017!2i3!3i16!2m3!1i2017!2i3!3i16)
New page, Inspect, Network, go to link, Copy as Curl

Get something like this:
curl 'https://www.google.com/maps/timeline/kml?authuser=0&pb=!1m8!1m3!1i2017!2i3!3i16!2m3!1i2017!2i3!3i16' 
-H 'accept-encoding: gzip, deflate, sdch, br' 
-H 'accept-language: en-US,en;q=0.8,fr;q=0.6' 
-H 'upgrade-insecure-requests: 1' 
-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36' 
-H 'x-chrome-uma-enabled: 1' 
-H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' 
-H 'authority: www.google.com' 
-H '**cookie**: gsScrollPos=; _ga=GA1.1.49937635TxMcGmJ-uXXXXX gsScrollPos=' 
-H 'x-client-data: XXXQ==' --compressed

save the cookie content
