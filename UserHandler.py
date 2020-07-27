from db import altDB
import main
from settings import database
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler
from simple_chalk import chalk
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton
from states import *
import telegram

END = ConversationHandler.END


def handle_user_menu(update, context):
    username = update.message.chat.username
    reply_keyboard = [['Create', 'Edit'],
                      ['Delete', 'Search'],
                      ['Back to Menu']]

    try:
        if find_user(username)['role'] == 'ADMIN':
            update.message.reply_text(
                "Welcome to user management dashboard",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return USER_ACTION

    except (TypeError):
        update.message.reply_text(
            """You are not a registered user or not an admin, do not have permission to manage users.
                """)
        done(update, context)
    except Exception as e:
        print(e)
        done(update, context)


def create_new_user(update, context):
    username = update.message.chat.username
    context.user_data['user-action'] = 'create'
    update.message.reply_text(
        'You have choose to create new user. Please enter your telegram username of user.',
        reply_markup=ReplyKeyboardMarkup(build_navigation_keyboard(), one_time_keyboard=True))
    return INPUT_USERNAME


def edit_user(update, context):
    username = update.message.chat.username
    context.user_data['user-action'] = 'edit'
    update.message.reply_text(
        'You have choose to edit current user. Please enter telegram username of user',
        reply_markup=ReplyKeyboardMarkup(build_navigation_keyboard(), one_time_keyboard=True))
    return INPUT_USERNAME


def handle_create_or_edit_user(update, context):
    action_type = context.user_data['user-action']
    if action_type == 'create':
        return create_new_user(update, context)
    if action_type == 'edit':
        return edit_user(update, context)
    else:
        handle_user_menu(update, context)


def handle_username(update, context):
    user = update.message.text
    context.user_data['input_username'] = user
    if find_user(user) or context.user_data['user-action'] == 'create':
        update.message.reply_text(
            'User\'s telegram username is {}. Please input the role: ADMIN, SELLER, CONSUMER'.format(
                user),
            reply_markup=ReplyKeyboardMarkup(build_user_role_keyboard(), one_time_keyboard=True))
        return INPUT_ROLE
    else:
        update.message.reply_text('User not found')
        return done(update, context)


def handle_role(update, context):
    text = update.message.text
    context.user_data['input_role'] = text
    reply_keyboard = [['CONFIRM'],
                      ['CANCEL']]

    if text not in ["ADMIN", "SELLER", "CONSUMER"]:
        update.message.reply_text("Invalid Role. Plase input role again")
        return handle_user_menu(update, context)
    else:
        reply = f"Username is *{context.user_data['input_username']}* and Role is {text}"
        update.message.reply_text(text=reply, reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, parse_mode=telegram.ParseMode.MARKDOWN))
        return userCONFIRMATION


def handle_confirmation(update, context):
    """[summary]
    Handle confirmation will parse contents stored in context and save it to DB.
    Remember to delete data from context after saving.
    """
    user = context.user_data['input_username']
    role = context.user_data['input_role']
    try:
        create_update_user(
            user, role)

        del context.user_data['input_username']
        del context.user_data['input_role']
        update.message.reply_text("Update saved")
    except Exception as e:
        print("error occured")
        update.message.reply_text("An error occurred")
        return ConversationHandler.END


"""
    TERMINAL OPERATIONS
"""


def handle_exit_to_main(update, context):
    main.start(update, context)
    return ConversationHandler.END


"""
UI Interface
"""


def build_user_role_keyboard():
    return [['ADMIN'], ['SELLER'], ['CONSUMER'], ['Back']]


def build_navigation_keyboard():
    return [['Back'], ['User Menu'], ['Main Menu']]


def build_confirmation_keyboard():
    return [['CONFIRM'], ['CANCEL'], ['Back']]


# Database operations
def find_user(username):
    return altDB.Users.find_one({'username': username})


def create_update_user(username, role):
    return altDB.Users.update(
        {'username': username},
        {'username': username, 'role': role}, upsert=True)

    """
    balance is only stored in user for caching purpose
    """


# def update_balance(username, newBalance):
#     return altDB.Users.update(
#         {'username': username},
#         {'$set':
#             {
#                 'balance': newBalance
#             }
#          }
#     )

    """
    User handler
    """


user_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(
        r'User Management'), handle_user_menu)],
    states={
        USER_ACTION: [MessageHandler(Filters.regex('^Create$'),
                                     create_new_user),
                      MessageHandler(Filters.regex('^Edit$'),
                                     edit_user),
                      MessageHandler(Filters.regex('^Back to Menu$'),
                                     handle_exit_to_main)
                      ],

        INPUT_USERNAME: [MessageHandler(Filters.regex('^Back$'),
                                        handle_user_menu),
                         MessageHandler(Filters.regex('^User Menu$'),
                                        handle_user_menu),
                         MessageHandler(Filters.regex('^Main Menu$'),
                                        handle_exit_to_main),
                         MessageHandler(Filters.text,
                                        handle_username)
                         ],

        INPUT_ROLE: [MessageHandler(Filters.regex('^Back$'),
                                    handle_create_or_edit_user),
                     MessageHandler(Filters.text,
                                    handle_role)
                     ],
        userCONFIRMATION: [MessageHandler(Filters.regex('^CONFIRM$'),
                                          handle_confirmation),
                           MessageHandler(Filters.regex('^CANCEL$'),
                                          handle_user_menu)
                           ],

    },

    fallbacks=[MessageHandler(Filters.regex('^/done$'), handle_exit_to_main)],
)
