#write in above stuff - cannot see on her vid so have guessed the below bar multiprocessing 
#also need to call the function - at end ?
import time
import datetime
import multiprocessing
import json
import csv
import gspread
import oauth2client
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os, sys

def weather_info():

    #Creating a timeout of 7 days - 24 hours, 60 min 60 seconds
    timeout = time.time() + 60 * 60 * 24 * 7 
    #timeout = time.time() + 120 
    #print('DIRECTORY', os.getcwd()) #this is where python is currently looking in. May need to change to my current path. 
    JSON_FILENAME = 'data.json'

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'] #first website refuses to open, the second just says the word 'drive'
    #I think this spreadsheets is now out of date. Bookmarked a website for new. The stackoverflow shows this text e x a c t l y lol. Try and find another. 
    #also do I need to set up googles authentication thing? 
    #scope = ['https://www.googleapis.com/auth/spreadsheets'] #first website refuses to open, the second just says the word 'drive'
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILENAME, scope) #I think this is where JSON is a 
    client = gspread.authorize(creds)
    sheet = client.open("Weather_data")
    ws  = sheet.get_worksheet(0) 
    ws.append_row(["Date", "Time", "City", "Weather", "Wind Speed", "Humidity", "Temperature"])


#response = requests.get(url)
#print(response.text)

    #{rint title on csv offline file for backup}
    with open('weather.csv', 'w', newline='') as f:
        headers = ["Date", "Time", "City", "Weather", "Wind Speed", "Humidity", "Temperature"]
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        while True:
            if time.time() > timeout:
                break
            elif time.time() < timeout:
                city_id = '2643743'
                my_id = '9c48d8525bc497c47f1e3d38b9023f56'
                r = requests.get('http://api.openweathermap.org/data/2.5/weather?id='+city_id+'&appid='+my_id+'')
                data = r.json()
                city = data['name']
                weather = data['weather'][0]['description']
                wind_speed = data['wind']['speed']
                humidity = float(data['main']['humidity'])
                temp_k = float(data['main']['humidity'])
                temp_c = (temp_k - 273.15)

                now = datetime.datetime.now()

                JSON_FILENAME = 'data.json'

                #google sheet saves gsq weather data

                scope = [] #what is this

                creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILENAME, scope)
                client = gspread.authorize(creds)
                sheet = client.open("Weather_data")
                ws  = sheet.get_worksheet(0) 
                ws.append_row([now.strftime("%d/%m/%Y"), now.strftime("%H:%M:%S"), city, weather, wind_speed, humidity, temp_c]) 

                w.writerow({'Date': now.strftime("%d/%m/%Y"), "Time": now.strftime("%H:%M:%S"), 'City':city, 'Weather': weather, 'Temperature': temp_c, 'Wind Speed': wind_speed, 'Humidity': humidity})
                
                #Wait for next, calculate every 15 mins
                time.sleep(60*15)


if __name__ == '__main__':
    weather = multiprocessing.Process(name= "weather", target = weather_info)
    weather.start()
