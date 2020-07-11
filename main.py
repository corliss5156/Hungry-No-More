from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from pymongo import MongoClient
import telegram

from order import stall, order_callback,item
from wallet import wallet
from recent_transactions import recent_transactions


Rules = """ 
Commands: 
/start      starts the bot 
/redeem     redeem credits 
/wallet     check balance in wallet
/recent_transactions    check last 5 transactions from wallet 
""" 

client = MongoClient("""mongodb+srv://Admin:admin123@cluster0-phjwg.mongodb.net/<dbname>?retryWrites=true&w=majority""")

database = client['Cluster0']

import logging
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
 
logger = logging.getLogger(__name__)

### STATES
MENU, TRANSACTION = range(2)


#Start command
def Start(bot, update):
    update.message.reply_text(Rules)


#Redeem command
def Redeem(update,context): 
    stall(update,context)
    return MENU

def Order_callback(update,context): 
    order_callback(update,context)
    return ConversationHandler.END


def Item(update,context):
    item(update,context)
    return TRANSACTION

#Wallet command
def Wallet(bot, update):
    wallet(bot,update)

#Recent Transactions command 
def Recent_Transactions(bot, update): 
    recent_transactions(bot,update)

### Main function
def main(): 
    updater = Updater('1202721044:AAGImDDtuW6IIZZVMxm6-65IzJjWFZfngOA', use_context=True)
    dp = updater.dispatcher

    #Command handlers
    dp.add_handler(CommandHandler("start", Start)) 
    dp.add_handler(CommandHandler("redeem", Redeem)) 
    dp.add_handler(CommandHandler("wallet", Wallet)) 
    dp.add_handler(CommandHandler("recent_transactions", Recent_Transactions))

    #Conversation Handler
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('redeem', Redeem)],
    states={
        MENU: [MessageHandler(Filters.regex('^'),Item)],
        TRANSACTION: [MessageHandler(Filters.regex('^'),CallbackQueryHandler)]
    },
    fallbacks=[CommandHandler('start', Start)],
    per_message = True
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()



##Giving money to someone else as admin 
##Household sending money to store
##Show store name 

##How much each menu item costs

##Ordering with confirm button 