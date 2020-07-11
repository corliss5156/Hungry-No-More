import pymongo
from settings import database


#Function to create new user with specified amount of credits 
def create_new_user(username, credits): 
    database.users.insert_one({'user': username, 'credits': credits})

#create_new_user('kaibing', 100)

#Function to create shop and its menu (in list)
def add_shop(name,items):
    database.shops.insert({'name':name,'items':items})
    
#add_shop('Pizza Lovers',[['Cheese Pizza',4],['Mushroom Pizza',10],['BBQ Chicken Pizza', 30],['Hawaiian Pizza',20]])

## GET MENU ITEMS
shopList = database['shops'].find()
for x in (shopList):
    for j in x['items']:
        print(j[0])