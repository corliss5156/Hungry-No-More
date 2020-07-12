import telegram 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import MongoClient, TEXT, DESCENDING
from datetime import datetime, timedelta
import re 
from settings import database


### Redeem function 
def stall(update,context): 
    shopList = database['shops'].find()
    button_list = []
    for x in (shopList):
        button_list.append(telegram.InlineKeyboardButton(x['name'],callback_data=x['name']))

    # button_list=[
    #     telegram.InlineKeyboardButton('Cheese Pizza',callback_data='Cheese_Pizza'),
    #     telegram.InlineKeyboardButton('Mushroom Pizza',callback_data='Mushroom_Pizza'),
    #     telegram.InlineKeyboardButton('Chicken Rice',callback_data='Chicken_Rice'),
    #     telegram.InlineKeyboardButton('Noodles',callback_data='Noodles'),
    #     telegram.InlineKeyboardButton('Wanton Noodles',callback_data='Wanton Noodles')
    # ]
    reply_markup=telegram.InlineKeyboardMarkup(build_menu(button_list,n_cols=1))
    context.bot.send_message(chat_id=update.message.chat_id, text='Choose from the following stores',reply_markup=reply_markup)


def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu   

def item(update,context):
    # update.message.reply_text('Maybe I can visit you sometime! '
    #                           'At last, tell me something about yourself.')
    item = update.callback_query.data
    shopList = database['shops'].find({'name': item})
    button_list = []
    for shop in (shopList):
        for menu in shop['items']:
            button_list.append(telegram.InlineKeyboardButton(menu[0],callback_data=menu[0]))
    reply_markup=telegram.InlineKeyboardMarkup(build_menu(button_list,n_cols=1))
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, text='Choose from the following items',reply_markup=reply_markup)
    

def order_callback(update,context): 
    username = update.message.chat.username
    item = update.message.text
    menu_item = re.sub('_', ' ', item)
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    
    context.bot.send_message(chat_id = update.callback_query.message.chat.id, text = "You ordered "+ menu_item + " at " + date)
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
