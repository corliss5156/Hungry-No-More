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
#add_shop('Western',[['Chicken Chope',7],['Steak',12],['Spaghetti',5]],'kaibing')

#Function to check user balance
def check_user_bal(name):
    database.users.find({'user':name})[0]['credits']

#Function to check shop balance
def topup_user_bal(username,add_credits): 
    new_credits =  database.users.find({'user':username})[0]['credits'] + add_credits
    database.users.replace_one({'user':username},{'user':username,'credits': new_credits}, upsert = False)

#test top up func
print(database.users.find({'user':'kaibing'})[0]['credits'])
topup_user_bal('kaibing',20)
print(database.users.find({'user':'kaibing'})[0]['credits'])
