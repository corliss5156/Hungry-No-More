from db import altDB
import re
import main
import TransactionHandler
import UserHandler
from settings import database
import telegram
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton
from simple_chalk import chalk
from states import *
from datetime import datetime

"""
Fund Handler
"""
"""
    # FUND PATH 1: MAKING DEPOSITS and WITHDRAWALS
"""


def handle_fund_menu(update, context):
    username = update.message.chat.username
    reply_keyboard = [['Make Deposit'],
                      ['Make Withdrawal'],
                      ['View Fund Balance'], ['Back']]

    update.message.reply_text(
        f"Welcome {username} to the fund management! What would you like to do?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return FUND_ACTION


def handle_withdrawal(update, context):
    context.user_data['fund_action'] = 'withdrawal'
    update.message.reply_text(
        'You have choose to make a withdrawal from fund. Please specify amount to withdrawal.',
        reply_markup=ReplyKeyboardMarkup(build_navigation_keyboard())
    )
    return FUND_AMOUNT


def handle_deposit(update, context):
    context.user_data['fund_action'] = 'deposit'
    update.message.reply_text(
        'You have choose to make a deposit to the fund. Please specify amount to deposit.',
        reply_markup=ReplyKeyboardMarkup(build_navigation_keyboard())
    )
    return FUND_AMOUNT


def handle_make_deposit_or_withdrawal(update, context):
    action_type = context.user_data['fund_action']
    if action_type == 'withdraw':
        return handle_withdrawal(update, context)
    if action_type == 'deposit':
        return handle_deposit(update, context)
    else:
        handle_fund_menu(update, context)


def handle_amount(update, context):
    amount = update.message.text
    action_type = context.user_data['fund_action']
    pattern = re.compile("^[1-9]\d*$")
    if amount == 'Back':
        amount = context.user_data['amount']
    if not pattern.match(amount):
        update.message.reply_text(
            "Invalid input amount")
        return handle_fund_menu(update, context)

    try:
        balance = check_fund_balance()
    except Exception as e:
        update.message.reply_text(
            "Error: Cannot read current balance at the moment. Please try again later")
        print(chalk.red("error in fund handle_amount"))
        return handle_fund_menu(update, context)
    if int(amount) > balance and action_type == 'withdrawal':
        update.message.reply_text(
            "Insufficient funds")
        return handle_fund_menu(update, context)

    if context.user_data['fund_action'] == 'withdrawal':
        message = f"Amount to withdraw: {amount} cents. Please specify which admin account to deduct from"
    elif context.user_data['fund_action'] == 'deposit':
        message = f"Amount to deposit: {amount} cents. Please specify which admin account to deposit to"
    update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(build_navigation_keyboard(), one_time_keyboard=True))

    # save to context
    context.user_data['amount'] = int(amount)

    # Next State
    return FUND_MANAGER


def handle_fund_manager(update, context):
    fund_manager = update.message.text
    if fund_manager == 'Back':
        fund_manager = context.user_data['fund_manager']
    try:
        response = UserHandler.find_user(fund_manager)
        if response:
            update.message.reply_text(
                f'Fund Manager\'s telegram username to deposit/withdraw from is {fund_manager}. Do you confirm?',
                reply_markup=ReplyKeyboardMarkup(
                    build_confirmation_keyboard(), one_time_keyboard=True)
            )
            context.user_data['fund_manager'] = fund_manager
            return FUND_CONFIRMATION
        else:
            update.message.reply_text(
                f'Admin: {fund_manager}. does not exist'.format(fund_manager))
            return handle_exit_to_main(update, context)

    except Exception as e:
        print(e)
        update.message.reply_text("An error occur in handle_transaction")


def handle_confirmation(update, context):
    action_by = update.message.chat.username
    action_type = context.user_data['fund_action']
    fund_manager = context.user_data['fund_manager']
    amount = context.user_data['amount']

    try:

        print('fund transaction successful',
              chalk.blue(create_fund_transaction(fund_manager, amount, action_type,
                                                 datetimeCreated=datetime.now(), action_by=action_by)))
    except Exception as e:
        print(
            chalk.red("Error in fund handle_confirmation, cannot create fund_transaction"))
        del context.user_data['fund_manager']
        del context.user_data['amount']
        del context.user_data['fund_action']
        return handle_fund_menu(update, context)
    try:
        if action_type == 'withdraw':
            TransactionHandler.createTransaction(
                fund_manager, 'fund', amount, 'fund withdrawal', datetime.now())

        if action_type == 'deposit':
            TransactionHandler.createTransaction(
                'fund', fund_manager, amount, 'fund deposit', datetime.now())
    except Exception as e:
        # clear context
        del context.user_data['fund_manager']
        del context.user_data['amount']
        del context.user_data['fund_action']
        print(Chalk.red('Error in fund handle_confirmation, cannot update transaction DB'))
        return handle_fund_menu(update, context)

    try:
        balance = check_fund_balance()
        message = f'Transaction Successful! Current fund balance/amount in circulation: {balance}'
        # Respond success
        update.message.reply_text(
            message)
        return handle_exit_to_main(update, context)
    except Exception as e:
        # Your balance cannot be updated!
        del context.user_data['fund_manager']
        del context.user_data['amount']
        del context.user_data['fund_action']
        print("Cannot read balance balance")


"""
    # TRANSACTION_PATH 2: View Balance
"""


def handle_show_balance(update, context):
    username = update.message.chat.username

    try:
        balance = check_fund_balance()
        message = f'Current balance: {balance}'
        # Respond success
        update.message.reply_text(
            message)
        return handle_exit_to_main(update, context)

    except Exception as e:
        print(chalk.red("ERROR: handle_show_balance"))
        print(e)


"""
    TERMINAL OPERATIONS
"""


def handle_exit_to_main(update, context):
    main.start(update, context)
    return ConversationHandler.END


"""
UI Interface
"""


def build_navigation_keyboard():
    return [['Back'], ['Fund Menu'], ['Main Menu']]


def build_confirmation_keyboard():
    return [['CONFIRM'], ['CANCEL'], ['Back']]


"""
Database Operations

"""


def create_fund_transaction(fund_manager, amount, action_type, datetimeCreated, action_by):
    assert amount >= 0
    assert action_type == 'withdraw' or action_type == 'deposit'
    return altDB.Funds.insert({'fund_manager': fund_manager, 'amount': amount, 'action_type': action_type,
                               'action_by': action_by,  'datetimeCreated': datetimeCreated})


# def retrieve_fund_history(username):
    # result = altDB.Funds.aggregate([
    #     {"$match": {"$or": [{"payer": {"$eq": username}},
    #                         {"payee": {"$eq": username}}]}},
    #     {"$limit": 5}
    # ])
    # return result


def check_fund_balance():
    amountWithdrawn = list(altDB.Funds.aggregate([{"$match": {"action_type": {"$eq": "withdraw"}}}, {
        "$group": {"_id": '', "amount": {"$sum": '$amount'}}}]))

    amountDeposited = list(altDB.Funds.aggregate([{"$match": {"action_type": {"$eq": "deposit"}}}, {
        "$group": {'_id': '', "amount": {"$sum": '$amount'}}}]))
    if not amountDeposited and not amountWithdrawn:
        return 0
    elif not amountDeposited:
        raise ValueError('Withdrawal exceeds deposit, DB values compromised')
    elif not amountWithdrawn:
        return int(list(amountDeposited)[0]['amount'])
    else:
        return int(list(amountDeposited)[0]['amount']) - int(list(amountWithdrawn)[0]['amount'])


def update_fund_transaction(fund_manager, amount, action_type, datetimeCreated, action_by):
    assert amount >= 0
    assert action_type == 'withdraw' or action_type == 'deposit'
    return altDB.Funds.update({'fund_manager': fund_manager, 'amount': amount, 'action_type': action_type,
                               'action_by': action_by,  'datetimeCreated': datetimeCreated})


fund_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(
        r'Fund Management'), handle_fund_menu)],
    states={
        FUND_ACTION: [MessageHandler(Filters.regex('^Make Withdrawal$'),
                                     handle_withdrawal),
                      MessageHandler(Filters.regex('^Make Deposit$'),
                                     handle_deposit),
                      MessageHandler(Filters.regex('^View Fund Balance$'),
                                     handle_show_balance),
                      #   MessageHandler(Filters.regex('^Fund History$'),
                      #                  handle_show_history),
                      MessageHandler(Filters.regex('^Back$'),
                                     handle_exit_to_main),
                      ],

        FUND_AMOUNT: [MessageHandler(Filters.regex('^Back$'),
                                     handle_fund_menu),
                      MessageHandler(Filters.regex('^Fund Menu$'),
                                     handle_fund_menu),
                      MessageHandler(Filters.regex('^Main Menu$'),
                                     handle_exit_to_main),
                      MessageHandler(Filters.text,
                                     handle_amount),
                      ],
        FUND_MANAGER: [MessageHandler(Filters.regex('^Back$'),
                                      handle_make_deposit_or_withdrawal),
                       MessageHandler(Filters.regex('^Fund Menu$'),
                                      handle_fund_menu),
                       MessageHandler(Filters.regex('^Main Menu$'),
                                      handle_exit_to_main),
                       MessageHandler(Filters.text,
                                      handle_fund_manager),
                       ],
        FUND_CONFIRMATION: [MessageHandler(Filters.regex('^CONFIRM$'),
                                           handle_confirmation),
                            MessageHandler(Filters.regex('^CANCEL$'),
                                           handle_exit_to_main),
                            MessageHandler(Filters.regex('^Back$'),
                                           handle_amount)
                            ],

    },

    fallbacks=[MessageHandler(Filters.regex(
        '^(/done|Main Menu)$'), handle_exit_to_main)],


)
