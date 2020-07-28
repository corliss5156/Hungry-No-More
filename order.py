import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup
from pymongo import MongoClient, TEXT, DESCENDING
from datetime import datetime, timedelta
import re
from settings import altDB
import json

bot = telegram.Bot(token="1202721044:AAGImDDtuW6IIZZVMxm6-65IzJjWFZfngOA")
with open('Menu_items.json') as json_file:
    DATA = json.load(json_file)


SHOPS, MENU, RECORD = range(0, 3)


def Reply_keyboard(store_name):
    reply_keyboard = []
    photos = []
    for item in altDB.Inventory.find({"name":store_name}, {"items": 1}): 
        for Item in item['items']:
            Menu_item = []
            menu_item = Item['item'] + ' $' + str(Item['price'])
            Menu_item.append(menu_item)
            photo = Item['image']
            reply_keyboard.append(Menu_item)
            photos.append(photo)
    reply_keyboard.insert(len(reply_keyboard), ['Back'])
    return reply_keyboard, photos


def order(update, context):
    reply_keyboard = []
    for store in altDB.Inventory.find({}, {"name": 1}): 
        name = []
        name.append(store['name'])
        reply_keyboard.append(name)
   
    update.message.reply_text('Choose store:', reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True))
    return SHOPS


def shops(update, context):
    reply_keyboard, photos = Reply_keyboard(update.message.text)
    context.chat_data['store'] = update.message.text
    update.message.reply_text('Chosen store is ' + update.message.text + '.\n Please choose an item from the menu.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    for i in range(0, len(photos)):
        bot.sendPhoto(chat_id = update.message.chat.id, photo= photos[i], caption = reply_keyboard[i][0])
    return MENU


def menu(update, context):
    reply_keyboard = [['Confirm and proceed to make payment'], ['Cancel']]
    text = re.split('[:]', update.message.text)
    info = altDB.Users.find_one({"username": update.message.chat.username})
    try:
        context.chat_data['order'] = text[0]
        context.chat_data['credits'] = text[-1]
        context.chat_data['user_credits'] = info['balance']
        update.message.reply_text('Chosen menu item is ' + text[0] + ' for ' + text[-1],
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    except:
        print(update)
        print("Error occured. Please try again.")
    # Store order

    return RECORD


def payment(update, context):
    print(update)
    if update.message.text == "Cancel":
        return ConversationHandler.END

    else:
        user = update.message.chat.username
        order_item = context.chat_data['order']
        store = context.chat_data['store']
        Credits = context.chat_data['credits']
        credit = re.split('[$]', Credits)
        credits = credit[-1]
        now = datetime.now()
        date = now.strftime("%d/%m/%Y %H:%M:%S")
        first_name = update.message.chat.first_name
        last_name = update.message.chat.last_name
        try: 
            user_data = altDB.Users.find_one({"username":user})
            if context.chat_data['user_credits']< int(credits)*100: 
                update.message.reply_text("Insufficient wallet balance. \n" +
                                      "Your remaining credits: " + str(context.chat_data['user_credits']))
                return ConversationHandler.END
            else:
                print("Sufficient wallet credits")
                try: 
                    altDB.Transactions.insert_one({"payer": user, "payee": store, "amount": int(credits)*100, "itemId": order_item, "datetimeCreated":date })
                    altDB.Users.update({"username": user}, {"$inc":{"balance":-int(credits)*100}})
                    update.message.reply_text("Order details: \n" + "Item: " + order_item +
                                      "\nStore: " + store + "\nPrice: " + credits + "\nOrder time: " + date)
                except: 
                    update.message.reply_text("Error processing transaction. Please try again.")

                try:
                    seller(user, store, order_item, date, first_name, last_name)
                except:
                    print("error occured")
                return ConversationHandler.END
        except:
            update.message.reply_text("You are not a user registered with us. Your order can not be processed")
            return ConversationHandler.END


def seller(buyer, seller, item, date, first_name, last_name):
    print(buyer, seller, item, date, first_name, last_name)
    seller_info = altDB.Inventory.find_one({"name": seller})
    try:
        bot.send_message(chat_id=seller_info['chatid'], text="Incoming order details: \n" + "Username: @" + buyer +
                     "\nCustomer: " + first_name + " " + last_name + "\nItem: " + item + "\nDate: " + date)
    except: 
        print('error')

