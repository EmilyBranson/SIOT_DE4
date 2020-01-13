import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
import openpyxl
import time
import datetime
import multiprocessing
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os, sys
import requests
import urllib.request
from urllib.request import urlopen
import json

class TwitterClass(object):  #this contains all the methods we are going to use to interact with the twitter API

    def __init__(self): #this is used to handle the authentication of the API client

        # keys and tokens from the Twitter Dev Console 
        with open('credsTwitter.txt') as json_file: #secret keys and access tokens saved offline
            CredsTwitter = json.load(json_file)
            consumer_key = CredsTwitter['consumer_key']
            consumer_secret = CredsTwitter['consumer_secret']
            access_token = CredsTwitter['access_token']
            access_token_secret = CredsTwitter['access_token_secret']

        # Then attempt Twitter authentication 
        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        except: 
            print("Error: Authentication Failed") 

    def clean_tweet(self, tweet): #this cleans the tweets of links and special characters
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\/\/\S+)", " ", tweet).split()) 

    def get_tweet_sentiment(self, tweet):  #this classes the tweet sentiment using textblob's sentiment method
        # create TextBlob object of passed tweet text 
        analysis = TextBlob(self.clean_tweet(tweet)) 
        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'

    def get_tweets(self, query, count = 10): #this gets twitter data containing certain words
        tweets = [] #this stores parsed tweets

        try: 
            fetched_tweets = self.api.search(q = query, count = count) #calls the twitter API to fetch tweets 

            for tweet in fetched_tweets: # parsing tweets one by one

                parsed_tweet = {} 
                parsed_tweet['text'] = tweet.text #saving tweet text
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) #saving tweet sentiment

                if tweet.retweet_count > 0: # appending parsed tweet to tweets list 
                    if parsed_tweet not in tweets: # if tweet has retweets, ensure that it is appended only once 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 

            return tweets #returns parsed tweets

        except tweepy.TweepError as e: 
            # print error (if any) 
            print("Error : " + str(e)) 

def main(): #main file which gathers all data togehter
    timeout = time.time() + 60 * 60 * 24 * 10 #running for 10 days worth of data collection

    while True:
        if time.time() > timeout: #if it goes beyond this 10 day time, break the while true loop
            break
        elif time.time() < timeout: 

            #Weather Dada from Open Weather Map API
            city_id = '2643743' #london id from the openweather website
            my_id = '9c48d8525bc497c47f1e3d38b9023f56' #OpenWeatherMap API Key
            r = requests.get('http://api.openweathermap.org/data/2.5/weather?id='+city_id+'&appid='+my_id+'')
            data = r.json()

            #weather data below collected from OpenWeatherMap for London
            city = data['name']
            weather = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            temp_k = float(data['main']['temp'])
            temp_c = (temp_k - 273.15)
            visibility = data['visibility']

            city_id = '2154855' #sydney id from the openweathermap website
            my_id = '9c48d8525bc497c47f1e3d38b9023f56'
            r2 = requests.get('http://api.openweathermap.org/data/2.5/weather?id='+city_id+'&appid='+my_id+'')
            data2 = r2.json()

            #weather data below collected from OpenWeatherMap for Sydney
            city2 = data2['name']
            weather2 = data2['weather'][0]['description']
            wind_speed2 = data2['wind']['speed']
            temp_k2 = float(data2['main']['temp'])
            temp_c2 = (temp_k2 - 273.15)
            visibility2 = data2['visibility']

            now = datetime.datetime.now()

            #Twitter Data from Twitter API London
            api = TwitterClass() # creating object of TwitterClient Class 
            tweets = api.get_tweets(query = 'climate change london', count = 200) # calling function to get tweets for climate change london
            notweets = len(tweets) # number of tweets about climate change

            ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] # picking positive tweets from tweets 
            pospercent = (100*len(ptweets)/len(tweets)) # percentage of positive tweets 

            ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] # picking negative tweets from tweets  
            negpercent = (100*len(ntweets)/len(tweets)) # percentage of negative tweets
             
            neutralpercent = 100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets) # percentage of neutral tweets

            #Twitter Data from Twitter API Sydney
            api = TwitterClass() # creating object of TwitterClient Class 
            tweets = api.get_tweets(query = 'climate change sydney', count = 200) # calling function to get tweets 
            notweets2 = len(tweets) # number of tweets about climate change
            
            ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] # picking positive tweets from tweets 
            pospercent2 = (100*len(ptweets)/len(tweets)) # percentage of positive tweets 
            
            ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] # picking negative tweets from tweets  
            negpercent2 = (100*len(ntweets)/len(tweets)) # percentage of negative tweets
             
            neutralpercent2 = 100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets) # percentage of neutral tweets
            
            #inserting the weather into the excel_insert function which appends the data into two google sheets, 'London' and 'Sydney'
            excel_insert(notweets, pospercent, negpercent, neutralpercent, notweets2, pospercent2, negpercent2, neutralpercent2, now.strftime("%d/%m/%Y"), now.strftime("%H:%M:%S"), city, weather, wind_speed, temp_c, visibility, city2, weather2, wind_speed2, temp_c2, visibility2)            
            
            #This opens the ThingSpeak url, where the data can be plotted live for subsequent use within the Web App
            #The data below is for temperature and positive and negative twitter sentiment for London
            urllib.request.urlopen("https://api.thingspeak.com/update?api_key=Q6FS4I9CT8HWYJMJ&field1="+str(temp_c))
            print("done")
            time.sleep(20) #ThingSpeak allows a maximum of one request per 15 seconds 
            urllib.request.urlopen("https://api.thingspeak.com/update?api_key=Q6FS4I9CT8HWYJMJ&field2="+str(pospercent))
            time.sleep(20)
            urllib.request.urlopen("https://api.thingspeak.com/update?api_key=Q6FS4I9CT8HWYJMJ&field3="+str(negpercent))
            time.sleep(20)

            #The data below is for temperature and positive and negative twitter sentiment for London
            urllib.request.urlopen("https://api.thingspeak.com/update?api_key=Q6FS4I9CT8HWYJMJ&field4="+str(temp_c2))
            time.sleep(20)
            urllib.request.urlopen("https://api.thingspeak.com/update?api_key=Q6FS4I9CT8HWYJMJ&field5="+str(pospercent2))
            time.sleep(20)
            urllib.request.urlopen("https://api.thingspeak.com/update?api_key=Q6FS4I9CT8HWYJMJ&field6="+str(negpercent2))
            time.sleep(20+8*60) #this delays the function by 10 minutes in total (with addition of the other 20 second sleeps in the lines above). 


def excel_insert(notweets, pospercent, negpercent, neutralpercent, notweets2, pospercent2, negpercent2, neutralpercent2, date, time, city, weather, wind_speed, temp_c, visibility, city2, weather2, wind_speed2, temp_c2, visibility2):
    #Authenticating the Google Sheets API so data can be appended
    scope = ['https://www.googleapis.com/auth/spreadsheets','https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope) #file which contains authorisation data 
    client = gspread.authorize(creds)
    now = datetime.datetime.now()

    #London Spreadsheet
    sheet = client.open("London")  
    ws = sheet.get_worksheet(0) 
    #Appending all weather and twitter data for London
    ws.append_row([notweets, pospercent, negpercent, neutralpercent, now.strftime("%m/%d/%Y"), now.strftime("%H:%M:%S"), city, weather, wind_speed, temp_c, visibility])

    #Sydney Spreadsheet
    sheet2 = client.open("Sydney")  
    ws = sheet2.get_worksheet(0) 
    #Appending all weather and twitter data for Sydney
    ws.append_row([notweets2, pospercent2, negpercent2, neutralpercent2, now.strftime("%m/%d/%Y"), now.strftime("%H:%M:%S"), city2, weather2, wind_speed2, temp_c2, visibility2]) 
    
          

if __name__ == '__main__':
    main()