import pymongo 
from settings import database
import telegram


def wallet(bot,update): 
    username = update.message.chat.username
    collection = list(database.users.find({'user': username}))
    credits = collection[0]['credits']
    bot.send_message(chat_id = update.message.chat_id, text = "Wallet balance: " + str(credits))
