import re
import requests
from requests_html import HTMLSession

from bs4 import BeautifulSoup
import pandas as pd
import datetime
from pymongo import MongoClient
import time
MONGO_URL="pass_in_your_link or just use 'localhost' "

client= MongoClient(MONGO_URL)
db = client.instagram_user



entities=['ronaldo', 'microsoft', 'messi', 'dell', 'lampard', 'pfizer', 'chelsea', 'sanofi', 'buhari', 'twitter']

#search=driver.find_element_by_name("q")
def get_all(entities):
    ##edit here later
    handle_every=[]
    name_every=[]
    #entities=['ronaldo', 'microsoft', 'messi', 'dell', 'lampard', 'pfizer', 'chelsea', 'sanofi', 'buhari', 'twitter']
    for ent in entities:
        try:
            url='https://searchusers.com/search/' + ent #'ukeme'
            print(url)

            session= HTMLSession()
            response=session.get(url)
            users=response.html.find('.timg')
            all_users=[a.text for a in users]

            all_list=[a.split('\n') for a in all_users]
            #print(all_list)

            handle_list=[item[0].strip('@') for item in all_list]

            name_list=[item[1] for item in all_list]

        except:
            pass

        handle_every.append(handle_list)
        name_every.append(name_list)
        
    return handle_every, name_every
    
    
def get_number_of_likes(handle_every): 
    ##get the number of likes for each handle   
        try:    
            handle_every=[b for a in handle_every for b in  a[:2]]
            num_of_likes=[]
            for j in handle_every:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


                    with requests.Session() as c:
                        url= 'https://searchusers.com/'+ 'user/' + j 
                        search=c.get(url, headers=headers)
                        soup = BeautifulSoup(search.content, 'html.parser')
                    
                        nposts2 = soup.findAll('div',  {'class': 'tallyb'}) ##get where the number of likes is called 
                    
                        nposts2=str(nposts2[1]) ##convert it to a string
                    
                        nposts2= re.findall(r'\d+', nposts2) ##get only the number
                        nposts2=int(''.join(nposts2)) ##convert it to an integer
                        print('....getting likes for....', j)
                        print()

                        num_of_likes.append(nposts2) ##append it to our empty list
                except:
                    num_of_likes.append(int(0)) ##append zero for users who locked their accounts
        except:
            pass
        #print(num_of_likes)
        return num_of_likes
        


        

        
def save_as_df(handle_every, name_every, num_of_likes):  
    
    handle_every=[b for a in handle_every for b in  a[:2]]
    name_every=[b for a in name_every for b in  a[:2]]
    
    ##save all to a dataframe       
    df=pd.DataFrame()
    df['handle']=handle_every
    df['full name']=name_every
    df['likes_per_post']=num_of_likes

    ##filter by a digit
    df=df[df['likes_per_post']>500]

    print(df)
    return df


def save_to_mongodb(df):
    
    
    # Load in the instagram_user collection from MongoDB
    instagram_user_collection = db.instagram_user_collection # similarly if 'testCollection' did not already exist, Mongo would create it
    
    cur = instagram_user_collection.find() ##check the number before adding
    print('We had %s instagram_user entries at the start' % cur.count())
    
     ##search for the entities in the processed colection and store it as a list
    instagram_users=list(instagram_user_collection.find({},{ "_id": 0, "handle": 1})) 
    instagram_users=list((val for dic in instagram_users for val in dic.values()))


    #loop throup the handles, and add only new enteries
    for handle in df['handle']:
        if handle  not in instagram_users:
            instagram_user_collection.insert_many(df.to_dict('records')) ####save the df to the collection
    
    
    
   
   
  
    cur = instagram_user_collection.find() ##check the number after adding
    print('We have %s spacy entity entries at the end' % cur.count())
    
    
   
def call_all_func(entities):
    #entities=['ronaldo', 'microsoft', 'messi', 'dell', 'lampard', 'pfizer', 'chelsea', 'sanofi', 'buhari', 'twitter']

    handle_every, name_every= get_all(entities)
    num_of_likes=get_number_of_likes(handle_every)
    df=save_as_df(handle_every, name_every, num_of_likes)
    save_to_mongodb(df)
    df = df.to_json()
    
    print('we are done ')
    
    return df
    
#call_all_func(entities)
