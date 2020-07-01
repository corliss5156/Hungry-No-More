from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import MongoClient
import telegram

from order import redeem, order_callback
from wallet import wallet
from recent_transactions import recent_transactions
from orderv2 import redeem2, order_callback2gi


Rules = """ 
Commands: 
/start      starts the bot 
/redeem     redeem credits 
/wallet     check balance in wallet
/recent_transactions    check last 5 transactions from wallet 
""" 

client = MongoClient("""mongodb+srv://Admin:admin123@cluster0-phjwg.mongodb.net/<dbname>?retryWrites=true&w=majority""")

database = client['Cluster0']




#Start command
def Start(bot, update):
    update.message.reply_text(Rules)


#Redeem command
def Redeem(bot,update): 
    redeem(bot,update)

def Order_callback(bot,update): 
    order_callback(bot, update)

#Wallet command
def Wallet(bot, update):
    wallet(bot,update)

#Recent Transactions command 
def Recent_Transactions(bot, update): 
    recent_transactions(bot,update)

### Main function
def main(): 
    updater = Updater('1202721044:AAGImDDtuW6IIZZVMxm6-65IzJjWFZfngOA')
    dp = updater.dispatcher

    #Command handlers
    dp.add_handler(CommandHandler("start", Start)) 
    dp.add_handler(CommandHandler("redeem", Redeem)) 
    dp.add_handler(CommandHandler("redeem2", Redeem2))
    dp.add_handler(CommandHandler("wallet", Wallet)) 
    dp.add_handler(CommandHandler("recent_transactions", Recent_Transactions))

    #Callback handlers
    dp.add_handler(telegram.ext.CallbackQueryHandler(Order_callback))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()



##Giving money to someone else as admin 
##Household sending money to store
##Show store name 

##How much each menu item costs

##Ordering with confirm button 