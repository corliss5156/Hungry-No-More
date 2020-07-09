import telegram 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import MongoClient, TEXT, DESCENDING
from datetime import datetime, timedelta
import re 
from settings import database


### Redeem function 
def redeem(bot,update): 
    
    button_list=[
        telegram.InlineKeyboardButton('Cheese Pizza',callback_data='Cheese_Pizza'),
        telegram.InlineKeyboardButton('Mushroom Pizza',callback_data='Mushroom_Pizza'),
        telegram.InlineKeyboardButton('Chicken Rice',callback_data='Chicken_Rice'),
        telegram.InlineKeyboardButton('Noodles',callback_data='Noodles'),
        telegram.InlineKeyboardButton('Wanton Noodles',callback_data='Wanton Noodles')
    ]
    reply_markup=telegram.InlineKeyboardMarkup(build_menu(button_list,n_cols=1))
    bot.send_message(chat_id=update.message.chat_id, text='Choose from the following',reply_markup=reply_markup)

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu   

def order_callback(bot,update): 
    username = update.callback_query.message.chat.username
    item = update.callback_query.data
    menu_item = re.sub('_', ' ', item)
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    
    bot.send_message(chat_id = update.callback_query.message.chat.id, text = "You ordered "+ menu_item + " at " + date)
    if item == 'Cheese_Pizza': 
        credits = 4
    elif item == 'Mushroom_Pizza': 
        credits = 10
    elif item == 'Chicken_Rice': 
        credits = 3
    elif item == 'Noodles': 
        credits = 5
    elif item == 'Wanton Noodles': 
        credits = 2
    deduct_credits(username, credits)
    record_transaction(username, credits, menu_item, date)

def record_transaction(username, credits, menu_item, date): 
    database.transactions.insert({'user': username, 'transaction': - credits, 'menu_item': menu_item, 'date': date})
    


def deduct_credits(user, credits): 
    database.users.update({'user': user},{'$inc':{'credits': -credits}})
