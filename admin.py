import pymongo
from settings import database


#Function to create new user with specified amount of credits 
def create_new_user(username, credits): 
    database.users.insert_one({'user': username, 'credits': credits})

#create_new_user('kaibing', 100)

#Function to create shop and its menu (in list)
def add_shop(name,items):
    nameList = []
    for i in items:
        nameList.append(i[0])
        database.items.insert({'itemName':i[0],'credits':i[1]})
    database.shops.insert({'name':name,'items':nameList})

#ADD STALL + ITEMS CREDITS
#add_shop('Doodle Noodles',[['Wanton Mee',8],['Curry Chicken Noodles',10],['Ban Mian',12],['Tomyum Noodles',12]])

## GET MENU ITEMS
# shopList = database['shops'].find()
# for x in (shopList):
#     for j in x['items']:
#         print(j)

#Get credits
item = database['items'].find({'itemName': 'Cheese Pizza'})
print(item[0]['credits'])
for x in item:
    print(x['credits'])