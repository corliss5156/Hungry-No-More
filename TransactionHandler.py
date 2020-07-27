from db import altDB
from simple_chalk import chalk
from telegram.ext import RegexHandler, ConversationHandler, Filters, MessageHandler
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton
from states import *
from datetime import datetime
import main
import re
import UserHandler
"""
TransactionHandler mananges trasaction between uses in the system

Operations

    Read Operations
        updateRunningBalance for User accout
        ReadTransactionHistory

    Create Operations
        makeTransaction
        Deposit: deposit from fund to admin balance
        Withdrawal: withdraw from admin balance

"""


"""
    # TRANSACTION_PATH 1: MAKE TRANSACTION
"""


def handle_transaction_menu(update, context):
    username = update.message.chat.username
    reply_keyboard = [['Make Transaction', 'View Balance'],
                      ['Transaction History', 'QR code'],
                      ['Back']]

    update.message.reply_text(
        f"Welcome {username} to the transactions dashboard! What would you like to do?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return TRANSACTION_ACTION

    """
        handle_payee used to handle event for specific telegram user.
        Todo: Implement proximity based payee selection
    """


def handle_make_transaction(update, context):
    update.message.reply_text(
        'You have choose to make a transaction. Please enter your telegram username of recepient.',
        reply_markup=ReplyKeyboardMarkup(build_navigation_keyboard())
    )
    return TRANSACTION_PAYEE


def handle_payee(update, context):
    username = update.message.chat.username
    payee = update.message.text
    if payee == 'Back':
        payee = context.user_data['payee']
    try:
        response = UserHandler.find_user(payee)
        if payee == username:
            update.message.reply_text(
                'You cannot make transactions to yourself!')
            return handle_exit_to_main(update, context)

        elif response:
            update.message.reply_text(
                f'Payee\'s telegram username is {payee}. Please specify amount to pay in cents. For $1, input: 100',
                reply_markup=ReplyKeyboardMarkup(
                    build_navigation_keyboard(), one_time_keyboard=True)
            )
            context.user_data['payee'] = payee
            return TRANSACTION_AMOUNT
        else:
            update.message.reply_text(
                f'Payee: {payee}. does not exist'.format(payee))
            return handle_exit_to_main(update, context)

    except Exception as e:
        print(chalk.blue("handle_payee"))
        print(e)
        update.message.reply_text("An error occur in handle_payee")


"""
TODO: Input validation for money format: Must be in cents. Else rerender message.
TODO: Input validation for amount, cannot exceed balance. Balance read from user cache.
TODO: Item to be selected from a dropdown menu with pagination maybe

"""


def handle_amount(update, context):
    amount = update.message.text
    pattern = re.compile("^[1-9]\d*$")
    username = update.message.chat.username

    if amount == 'Back':
        amount = context.user_data['amount']
    if not pattern.match(amount):
        update.message.reply_text(
            "Invalid input amount")
        return handle_transaction_menu(update, context)

    try:
        balance = checkRunningBalance(username)
    except Exception as e:
        update.message.reply_text(
            "Error: Cannot read current balance at the moment. Please try again later")
        print(chalk.red("error in transaction handle_amount"))
        return handle_transaction_menu(update, context)

    if int(amount) > balance:
        update.message.reply_text(
            f"Insufficient funds, for transaction. You only have{balance}, please seek an admin for top up or make deposit to fund to your account")
        return handle_transaction_menu(update, context)

    message = f"Amount to transfer: {amount} cents. Please specify item ID/Description"
    update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(build_navigation_keyboard(), one_time_keyboard=True))

    # save to context
    context.user_data['amount'] = int(amount)

    # Next State
    return TRANSACTION_ITEM


"""
    item is currently a description of type String
    TODO: Item should be stored as inventoryID. Selected from a dropdown menu with pagination maybe
"""


def handle_item(update, context):
    itemDesc = update.message.text
    if itemDesc == 'Back':
        itemDesc = context.user_data['itemDesc']
    message = f"Confirm Transaction?\n"\
        f"PAYEE: {context.user_data['payee']}\n"\
        f"AMOUNT: {context.user_data['amount']}\n"\
        f"Item desc: {itemDesc}.\n Confirm Transaction"\

    update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(build_confirmation_keyboard(), one_time_keyboard=True))

    # save to context
    context.user_data['itemDesc'] = itemDesc

    # Next State
    return TRANSACTION_CONFIRMATION


def handle_confirmation(update, context):
    try:

        username = update.message.chat.username
        payee = context.user_data['payee']
        amount = context.user_data['amount']
        itemDesc = context.user_data['itemDesc']
        print(createTransaction(username, payee, amount,
                                itemId=itemDesc, datetimeCreated=datetime.now()))

        # clear context

        del context.user_data['payee']
        del context.user_data['amount']
        del context.user_data['itemDesc']

        try:
            balance = checkRunningBalance(username)

            message = f'Transaction Successful! Current balance: {balance}'
            # Respond success
            update.message.reply_text(
                message)
            return handle_exit_to_main(update, context)
        except Exception as e:
            # Your balance cannot be updated!
            print("Cannot read balance or update cached balance")

    except Exception as e:
        print(e)


"""
    # TRANSACTION_PATH 2: View Balance
"""


def handle_show_balance(update, context):
    username = update.message.chat.username

    try:
        balance = checkRunningBalance(username)
        message = f'Current balance: {balance}'
        # Respond success
        update.message.reply_text(
            message)
        return handle_exit_to_main(update, context)

    except Exception as e:
        print(chalk.red("ERROR: handle_show_balance"))
        print(e)


"""
    # TRANSACTION_PATH 3: View Transaction History
"""


def handle_show_history(update, context):
    username = update.message.chat.username

    try:
        transactions = retrievePastTransactions(username)
        message = "Last 5 Transactions:\n=================================\n"

        for transaction in transactions:
            message += format_transaction(username, transaction)
            message += "\n"
        # Respond success
        update.message.reply_text(
            message)
        return handle_exit_to_main(update, context)

    except Exception as e:
        print(chalk.red("ERROR: handle_show_balance"))
        print(chalk.red(e))


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
    return [['Back'], ['Transaction Menu'], ['Main Menu']]


def build_confirmation_keyboard():
    return [['CONFIRM'], ['CANCEL'], ['Back']]


def format_transaction(username, transaction):
    if transaction["payee"] == username:
        return f"From:{transaction['payer']}\nItem: {transaction['itemId']}\nAmount: +{transaction['amount']}\n{transaction['datetimeCreated']}\n"

    elif transaction["payer"] == username:
        return f"Pay To: {transaction['payee']}\nItem: {transaction['itemId']}\nAmount: -{transaction['amount']}\n{transaction['datetimeCreated']}\n"


"""
Database Operations

"""


def retrievePastTransactions(username):
    result = altDB.Transactions.aggregate([
        {"$match": {"$or": [{"payer": {"$eq": username}},
                            {"payee": {"$eq": username}}]}},
        {"$limit": 5}
    ])
    return result


def createTransaction(payer, payee, amount, itemId, datetimeCreated):
    assert payer != payee
    return altDB.Transactions.insert({'payer': payer, 'payee': payee, 'amount': amount,
                                      'itemId': itemId,  'datetimeCreated': datetimeCreated})


def checkRunningBalance(username):
    amountPaid = list(altDB.Transactions.aggregate([{"$match": {"payer": {"$eq": f"{username}"}}}, {
        "$group": {"_id": '', "amount": {"$sum": '$amount'}}}]))

    amountReceived = list(altDB.Transactions.aggregate([{"$match": {"payee": {"$eq": f"{username}"}}}, {
        "$group": {'_id': '', "amount": {"$sum": '$amount'}}}]))

    if not amountPaid and not amountReceived:
        return 0
    elif not amountReceived:
        raise ValueError('Paid more than received')
    elif not amountPaid:
        return int(list(amountReceived)[0]['amount'])
    else:
        return int(list(amountReceived)[0]['amount']) - int(list(amountPaid)[0]['amount'])


def updateTransaction(payer, payee, amount, itemId, datetimeCreated):
    return altDB.Transactions.update(
        {'_id': id},
        {'payer': payer, 'payee': payee, 'amount': amount, 'itemId': itemId,  'datetimeCreated': datetimeCreated}, upsert=True)


"""
Transaction Handler
"""

transaction_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(
        r'Transactions'), handle_transaction_menu)],
    states={
        TRANSACTION_ACTION: [MessageHandler(Filters.regex('^Make Transaction$'),
                                            handle_make_transaction),
                             MessageHandler(Filters.regex('^View Balance$'),
                                            handle_show_balance),
                             MessageHandler(Filters.regex('^Transaction History$'),
                                            handle_show_history),
                             MessageHandler(Filters.regex('^Back$'),
                                            handle_exit_to_main),
                             ],

        TRANSACTION_PAYEE: [MessageHandler(Filters.regex('^Back$'),
                                           handle_transaction_menu),
                            MessageHandler(Filters.regex('^Transaction Menu$'),
                                           handle_transaction_menu),
                            MessageHandler(Filters.regex('^Main Menu$'),
                                           handle_exit_to_main),
                            MessageHandler(Filters.text,
                                           handle_payee),
                            ],
        TRANSACTION_AMOUNT: [MessageHandler(Filters.regex('^Back$'),
                                            handle_make_transaction),
                             MessageHandler(Filters.regex('^Transaction Menu$'),
                                            handle_transaction_menu),
                             MessageHandler(Filters.regex('^Main Menu$'),
                                            handle_exit_to_main),
                             MessageHandler(Filters.text,
                                            handle_amount),
                             ],
        TRANSACTION_ITEM: [MessageHandler(Filters.regex('^Back$'),
                                          handle_payee),
                           MessageHandler(Filters.regex('^Transaction Menu$'),
                                          handle_transaction_menu),
                           MessageHandler(Filters.regex('^Main Menu$'),
                                          handle_exit_to_main),
                           MessageHandler(Filters.text,
                                          handle_item),
                           ],
        TRANSACTION_CONFIRMATION: [MessageHandler(Filters.regex('^CONFIRM$'),
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
