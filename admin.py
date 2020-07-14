import pymongo
from settings import database


#Function to create new user with specified amount of credits 
def create_new_user(username, credits): 
    database.users.insert_one({'user': username, 'credits': credits})

#create_new_user('kaibing', 100)

#Function to create shop and its menu (in list)
def add_shop(name,items,username):
    products = []
    for i in items:
        products.append({'item':i[0],'price':i[1]})
    database.shops.insert({'username':username,'name':name,'items':products, 'chatid':None, 'location': None})

#ADD STALL + ITEMS CREDITS
add_shop('Western',[['Chicken Chope',7],['Steak',12],['Spaghetti',5]],'kaibing')

## GET MENU ITEMS
# shopList = database['shops'].find()
# for x in (shopList):
#     for j in x['items']:
#         print(j)

#Get credits
# item = database['items'].find({'itemName': 'Cheese Pizza'})
# print(item[0]['credits'])
# for x in item:
#     print(x['credits'])