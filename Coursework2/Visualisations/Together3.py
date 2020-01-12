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
from pprint import pprint
import requests


def weather_info():

    #Creating a timeout of 7 days - 24 hours, 60 min 60 seconds
    timeout = time.time() + 60 * 60 * 24 * 7 

    scope = ['https://www.googleapis.com/auth/spreadsheets','https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Twitter")

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

            scope = ['https://www.googleapis.com/auth/spreadsheets','https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
            client = gspread.authorize(creds)
            sheet = client.open("Twitter")
            ws = sheet.get_worksheet(0) 
            ws.append_row(['', '', '', '', now.strftime("%d/%m/%Y"), now.strftime("%H:%M:%S"), city, weather, wind_speed, humidity, temp_c]) 

            time.sleep(60)

class TwitterClient(object):  #this contains all the methods we are going to use to interact with the twitter API
    ''' 
    Generic Twitter Class for sentiment analysis. 
    '''
    def __init__(self): #this is used to handle the authentication of the API client
        ''' 
        Class constructor or initialization method. 
        '''
        # keys and tokens from the Twitter Dev Console 
        consumer_key = 'HNkWCJNGQU6Bk6cxilum0gMr0'
        consumer_secret = '1886K2v6rmqrXPmg3g5sb8QpCc22cHXYzPJqulvqhzJPpDiBTu'
        access_token = '1210937961727946754-zGlCFew3lzYyJrCeBieolwx2JCq5cp' #need to put these in a secret file. 
        access_token_secret = '9e5AEccpD3sy7tWNFhwqk3yloE3W6Z4T6hD9LombRDqbk'

        # attempt authentication 
        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        except: 
            print("Error: Authentication Failed") 

    def clean_tweet(self, tweet): 
        ''' 
        Utility function to clean tweet text by removing links, special characters 
        using simple regex statements. 
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\/\/\S+)", " ", tweet).split()) 

    def get_tweet_sentiment(self, tweet):  
        ''' 
        Utility function to classify sentiment of passed tweet 
        using textblob's sentiment method 
        '''
        # create TextBlob object of passed tweet text 
        analysis = TextBlob(self.clean_tweet(tweet)) 
        #this is 
        
        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'

    def get_tweets(self, query, count = 10): 
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets 
        tweets = [] 

        try: 
            # call twitter api to fetch tweets 
            fetched_tweets = self.api.search(q = query, count = count) 
            #the above calls the twitter API to fetch tweets 
            
            # parsing tweets one by one 
            for tweet in fetched_tweets: 
                # empty dictionary to store required params of a tweet 
                parsed_tweet = {} 

                # saving text of tweet 
                parsed_tweet['text'] = tweet.text 
                # saving sentiment of tweet 
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 

                # appending parsed tweet to tweets list 
                if tweet.retweet_count > 0: 
                    # if tweet has retweets, ensure that it is appended only once 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 

            # return parsed tweets 
            return tweets 

        except tweepy.TweepError as e: 
            # print error (if any) 
            print("Error : " + str(e)) 

def main(): 
    timeout = time.time() + 60 * 60 * 24 * 7 

    while True:
        if time.time() > timeout:
            break
        elif time.time() < timeout: 
            #time.sleep(1)
            # creating object of TwitterClient Class 
            api = TwitterClient() 
            # calling function to get tweets 
            tweets = api.get_tweets(query = 'climate change', count = 200) 

            # picking positive tweets from tweets 
            ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
            # percentage of positive tweets 
            print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
            pospercent = (100*len(ptweets)/len(tweets))
            
            # picking negative tweets from tweets 
            ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
            # percentage of negative tweets 
            print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
            negpercent = (100*len(ntweets)/len(tweets))
            
            # percentage of neutral tweets 
            print("Neutral tweets percentage: {} %".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets))) 
            neutralpercent = 100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)
            
            #scope = ['https://www.googleapis.com/auth/spreadsheets','https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
            #creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
            #client = gspread.authorize(creds)
            #spreadsheet = client.open("Twitter") #it thinks sheet is a worksheet. Should think it's a spreadsheet. 
            #ws = spreadsheet.get_worksheet(0) #this is wrong atm. 
            #ws.append_row([pospercent, negpercent, neutralpercent]) 
            #worksheet = client.open("Twitter").sheet1
            #spreadsheet.move_range("A3:C3", rows=-1)
            #sheet.append_row([pospercent, negpercent, neutralpercent])

            # printing first 5 positive tweets 
            print("\n\nPositive tweets:") 
            for tweet in ptweets[:10]: 
                print(tweet['text']) 

            # printing first 5 negative tweets 
            print("\n\nNegative tweets:") 
            for tweet in ntweets[:10]: 
                print(tweet['text']) 
            
            excel_insert(pospercent, negpercent, neutralpercent)
            time.sleep(60)
            #return pospercent, negpercent, neutralpercent

def excel_insert(pospercent, negpercent, neutralpercent):
    scope = ['https://www.googleapis.com/auth/spreadsheets','https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Twitter") #it thinks sheet is a worksheet. Should think it's a spreadsheet. 
    ws = spreadsheet.get_worksheet(0) #this is wrong atm. 
    ws.append_row([pospercent, negpercent, neutralpercent]) 


if __name__ == '__main__':
    weather = multiprocessing.Process(name= "weather", target = weather_info)
    twitter = multiprocessing.Process(name= "twitter", target = main)

    weather.start()
    twitter.start()
    #x = excel_insert() #not sure
