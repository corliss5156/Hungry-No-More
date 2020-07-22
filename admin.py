import pymongo
from settings import database
import telegram 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup

bot = telegram.Bot(token = "1202721044:AAGImDDtuW6IIZZVMxm6-65IzJjWFZfngOA")

CHOOSE,NEW_USER,NEW_SHOP,TOP_UP,CHECK_BAL = range(0,5)

def admin(update,context):
    reply_keyboard = [['Add New User', 'Add New Shop', 'Top-up User Credits','Check User Balance']]
    update.message.reply_text('Hi Admin User! What would you like to do today?', reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CHOOSE

def choose(update,context):
    if update.message.text == "Add New User":
        update.message.reply_text(
        "Input username and amount of credits to be added"
        "\nPlease answer the questions in this format: user,credits."
        "\nE.g Tom,100")
        return NEW_USER
    if update.message.text == "Add New Shop":
        update.message.reply_text(
        "The following information is required: \n1) Shop owner's telegram handle \n2) Shop name, \n3) Items sold in the shop and their respective credits"
        "\n\nPlease provide the details in this format: Shop Owner,Shop Name,[[Item #1,Amount of credits for Item #1],[Item #2,Amount of credits for Item #2]]"
        "\nE.g Tom,Tom's Eatery,[Chicken Rice,8],[Tom's Special,10]")
        return NEW_SHOP
    if update.message.text == "Top-up User Credits":
        update.message.reply_text(
        "Input username and amount to top-up"
        "\nPlease answer the questions in this format: user,top-up amount."
        "\nE.g Tom,50")
        return TOP_UP
    if update.message.text == "Check User Balance":
        update.message.reply_text(
        "Input username")
        return CHECK_BAL

def create_new_user(update, context):
    text = update.message.text.split(",")
    database.users.insert_one({'user': text[0], 'credits': int(text[1])})
    update.message.reply_text(
        text[0] + " has been added into the system with " + text[1] + " credits")
    return ConversationHandler.END
           
def create_new_shop(update,context):
    text = update.message.text.split("[",1)
    front = text[0].split(",")
    items = text[1].split("],[")
    items[-1] = items[-1].split("]")[0]
    products = []
    for i in items:
        item = i.split(",")
        products.append({'item':item[0],'price':int(item[1])})
    database.shops.insert({'username':front[0],'name':front[1],'items':products, 'chatid':None, 'location': None})
    update.message.reply_text(
        front[1] + " has been added into the system" ) 
    return ConversationHandler.END

def topup_user_bal(update,context):
    text = update.message.text.split(",") 
    #check if user exist
    if database.users.find({'user':text[0]}).count() > 0:
        new_credits =  database.users.find({'user':text[0]})[0]['credits'] + int(text[1])
        database.users.replace_one({'user':text[0]},{'user':text[0],'credits': new_credits}, upsert = False)
        update.message.reply_text(text[1] + " credits has been added to " + text[0] + "'s account")
    else:
        update.message.reply_text(text[0] + " is not a user in the system")
    return ConversationHandler.END

def check_user_bal(update,context):
    name = update.message.text
    if database.users.find({'user':name}).count() > 0:
        credits = database.users.find({'user':name})[0]['credits']
        update.message.reply_text(
            name + " has " + str(credits) + " in his/her wallet")
    else:
        update.message.reply_text(name + " is not a user in the system")
    return ConversationHandler.END

# ### Adding using py file
# #Function to create new user with specified amount of credits 
# def create_new_user(username, credits): 
#     database.users.insert_one({'user': username, 'credits': credits})

# #create_new_user('kaibing', 100)

# #Function to create shop and its menu (in list)
# def add_shop(name,items,username):
#     products = []
#     for i in items:
#         products.append({'item':i[0],'price':i[1]})
#     database.shops.insert({'username':username,'name':name,'items':products, 'chatid':None, 'location': None})

# #ADD STALL + ITEMS CREDITS
# #add_shop('Western',[['Chicken Chope',7],['Steak',12],['Spaghetti',5]],'kaibing')

# #Function to check user balance
# def check_user_bal(name):
#     database.users.find({'user':name})[0]['credits']

# #Function top up user balance
# def topup_user_bal(username,add_credits): 
#     new_credits =  database.users.find({'user':username})[0]['credits'] + add_credits
#     database.users.replace_one({'user':username},{'user':username,'credits': new_credits}, upsert = False)

# #test top up func
# print(database.users.find({'user':'kaibing'})[0]['credits'])
# topup_user_bal('kaibing',20)
# print(database.users.find({'user':'kaibing'})[0]['credits'])
