from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup
import telegram
from states import *
import logging
import UserHandler
import TransactionHandler
import InventoryHandler
import FundHandler
from settings import API_TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Start command
"brief instructions and guide "


def start(update, context):
    username = update.message.chat.username
    # update.message.reply_text(Rules)
    # Check is admin/consumer/shop OR unregistered
    reply_keyboard = [
        ['Transactions','Send My Location'],
        ['Shop Management'],
        ['User Management'],
        ['Fund Management']
    ]
    update.message.reply_text(
        f"Welcome {username}! What would you like to do?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return MAIN_SELECT


def main():
    updater = Updater(
       '1202721044:AAGImDDtuW6IIZZVMxm6-65IzJjWFZfngOA', use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(UserHandler.user_handler)
    dp.add_handler(TransactionHandler.transaction_handler)
    dp.add_handler(InventoryHandler.shop_handler)
    dp.add_handler(FundHandler.fund_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
