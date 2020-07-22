from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup
from pymongo import MongoClient
import telegram
from order import order, shops, menu, record 
from wallet import wallet
from recent_transactions import recent_transactions
from admin import admin,choose,create_new_user,create_new_shop,topup_user_bal,check_user_bal

import logging

#Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


Rules = """ 
Commands: 
/start      starts the bot 
/order      order 
/wallet     check balance in wallet
/recent_transactions    check last 5 transactions from wallet 
""" 

client = MongoClient("""mongodb+srv://Admin:admin123@cluster0-phjwg.mongodb.net/<dbname>?retryWrites=true&w=majority""")

database = client['Cluster0']

SHOPS, MENU,RECORD = range(0,3)
CHOOSE,NEW_USER,NEW_SHOP,TOP_UP,CHECK_BAL = range(0,5)


#Start command
def Start(update, context):
    update.message.reply_text(Rules)



### Main function
def main(): 
    updater = Updater('1202721044:AAGImDDtuW6IIZZVMxm6-65IzJjWFZfngOA', use_context=True)
    dp = updater.dispatcher

    #Ordering handlers
    order_handler = ConversationHandler(
    entry_points = [CommandHandler('order', order)], 
    states = {
        SHOPS: [MessageHandler(Filters.regex('^(Pizza|Chinese)$'),shops)], 
        MENU: [MessageHandler(Filters.regex('^'), menu)], 
        RECORD: [MessageHandler(Filters.regex('^'), record)]
        }, fallbacks = [CommandHandler('cancel', Start)])

    #Admin Settings
    admin_handler = ConversationHandler(
    entry_points = [CommandHandler('admin', admin)], 
    states = {
        CHOOSE: [MessageHandler(Filters.regex('^'),choose)], 
        NEW_USER: [MessageHandler(Filters.regex('^'), create_new_user)],
        NEW_SHOP: [MessageHandler(Filters.regex('^'), create_new_shop)],
        TOP_UP: [MessageHandler(Filters.regex('^'), topup_user_bal)],
        CHECK_BAL: [MessageHandler(Filters.regex('^'), check_user_bal)]
        }, fallbacks = [CommandHandler('cancel', Start)])
   
    #Command handlers
    dp.add_handler(CommandHandler("cancel", Start)) 
    dp.add_handler(order_handler)
    dp.add_handler(admin_handler)

    
    
   
    dp.add_handler(CommandHandler('Start', Start))
    dp.add_handler(CommandHandler("wallet", wallet)) 
    dp.add_handler(CommandHandler("recent_transactions", recent_transactions))



   

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


