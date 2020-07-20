import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup
from pymongo import MongoClient, TEXT, DESCENDING
from datetime import datetime, timedelta
import re
from settings import database
import json

bot = telegram.Bot(token="1202721044:AAGImDDtuW6IIZZVMxm6-65IzJjWFZfngOA")
with open('Menu_items.json') as json_file:
    DATA = json.load(json_file)


SHOPS, MENU, RECORD = range(0, 3)


def Reply_keyboard(store_name):
    reply_keyboard = [[]]
    for item in DATA[store_name]['Products']:
        menu_item = item['Item'] + ': $' + str(item['Price'])
        reply_keyboard[0].append(menu_item)
    return reply_keyboard


def order(update, context):
    reply_keyboard = [['Pizza', 'Chinese']]
    print(chalk.green(context))
    update.message.reply_text('Choose store:', reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True))
    return SHOPS


def shops(update, context):
    print(chalk.red(update.message))
    reply_keyboard = Reply_keyboard(update.message.text)
    context.chat_data['store'] = update.message.text
    update.message.reply_text('Chosen store is ' + update.message.text + '.\n Please choose an item from the menu.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    print(update)
    return MENU


def menu(update, context):
    reply_keyboard = [['Confirm', 'Cancel']]
    text = re.split('[:]', update.message.text)
    info = database.users.find_one({"user": update.message.chat.username})
    try:
        context.chat_data['order'] = text[0]
        context.chat_data['credits'] = text[-1]
        context.chat_data['user_credits'] = info['credits']
        print(context.chat_data)
        update.message.reply_text('Chosen menu item is ' + text[0] + ' for ' + text[-1],
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    except:
        print(update)
        print("Error occured. Please try again.")
    # Store order

    return RECORD


def record(update, context):
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
        if context.chat_data['user_credits'] < int(credits):
            update.message.reply_text("Insufficient wallet balance. \n" +
                                      "Your remaining credits: " + str(context.chat_data['user_credits']))
            return ConversationHandler.END
        else:
            print("Sufficient wallet credits")
            update.message.reply_text("Order details: \n" + "Item: " + order_item +
                                      "\nStore: " + store + "\nPrice: " + credits + "\nOrder time: " + date)
            try:
                record_transaction_buyer(
                    user, int(credits), store, order_item, date)
                record_transaction_seller(user, int(credits), order_item, date)
                deduct_credits(user, int(credits))
                print("success")
                try:
                    seller(user, store, order_item,
                           date, first_name, last_name)
                except:
                    print(user, store, order_item, date)
                    print("Transaction did not pass through")
            except:
                print("error occured")
            return ConversationHandler.END
        # order_item = bot.user_data[update.message.chat.username]

        # update.message.reply_text("Order details:" + '\ Item: ' + menu_ti)


def seller(buyer, seller, item, date, first_name, last_name):
    seller_id = DATA[seller]["chatid"]
    bot.send_message(chat_id=seller_id, text="Incoming order details: \n" + "Username: @" + buyer +
                     "\nCustomer: " + first_name + " " + last_name + "\nItem: " + item + "\nDate: " + date)


def record_transaction_buyer(username, credits, store, menu_item, date):
    database.buyer_transactions.insert(
        {'user': username, 'transaction': - credits, 'store': store, 'menu_item': menu_item, 'date': date})


def record_transaction_seller(username, credits, menu_item, date):
    database.seller_transactions.insert(
        {'user': username, 'transactions': + credits, 'menu_item': menu_item, 'date': date})


def deduct_credits(user, credits):
    database.users.update({'user': user}, {'$inc': {'credits': -credits}})
