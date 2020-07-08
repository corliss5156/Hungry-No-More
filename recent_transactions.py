import pymongo 
from settings import database
import telegram

def recent_transactions(update,context): 
    username = update.message.chat.username
    collections = list(database.transactions.find({'user':username}).sort([("date", 1)]).limit(5))
    transactions = 'Your recent transations: ' +'\n'
    for collection in reversed(collections):
        transactions += collection['menu_item'] + " : " + collection['date'] + '\n'

    update.message.reply_text(transactions)
