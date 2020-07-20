from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup
import telegram
from order import order, shops, menu, record
from recent_transactions import recent_transactions
from states import *
import logging
import UserHandler
import TransactionHandler
from settings import API_TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Rules = """
# Commands:
# /start      starts the bot
# /user       Enter user menu
# /transactions Transactions
# /order      order
# /recent_transactions    check last 5 transactions from wallet
# """


# Start command
"brief instructions and guide "


def start(update, context):
    username = update.message.chat.username
    # update.message.reply_text(Rules)
    reply_keyboard = [['User Management'],
                      ['Transactions'],
                      ['Send My Location']
                      ]
    update.message.reply_text(
        f"Welcome {username}! What would you like to do?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return MAIN_SELECT


def main():
    updater = Updater(
        API_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Ordering handlers
    # order_handler = ConversationHandler(
    #     entry_points=[CommandHandler('order', order)],
    #     states={
    #         SHOPS: [MessageHandler(Filters.regex('^(Pizza|Chinese)$'), shops)],
    #         MENU: [MessageHandler(Filters.regex('^'), menu)],
    #         RECORD: [MessageHandler(Filters.regex('^'), record)]
    #     }, fallbacks=[CommandHandler('cancel', start)])
    # dp.add_handler(order_handler)
    # dp.add_handler(CommandHandler("recent_transactions", recent_transactions))

    # Command handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(UserHandler.user_handler)
    dp.add_handler(TransactionHandler.transaction_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
