import pymongo 
from settings import database
import telegram


def wallet(update,context): 
    username = update.message.chat.username
    collection = list(database.users.find({'user': username}))
    credits = collection[0]['credits']
    update.message.reply_text("Wallet balance: " + str(credits))

bot = telegram.Bot(token = "1342752441:AAH12-Q914sRWKRWMfOv6g_1_gVtIHXL9L0")

# bot.send_message(chat_id = 'corlaze', text = 'here')