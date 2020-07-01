import pymongo 
from settings import database
import telegram

def recent_transactions(bot, update): 
    username = update.message.chat.username
    collections = list(database.transactions.find({'user':username}).limit(5))
    transactions = 'Your recent transations: ' +'\n'
    for collection in collections:
        transactions += collection['menu_item'] + " : " + collection['date'] + '\n'

    bot.send_message(chat_id = update.message.chat_id, text = transactions)
