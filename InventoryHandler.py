from db import altDB
import main
from settings import database
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton
from states import *
import telegram

def handle_shop_menu(update, context):
    username = update.message.chat.username
    reply_keyboard = [['Add Item', 'Delete Item'],
                      ['View My Store Items','Back to Menu']]

    try:
        if (find_user(username)['role'] == 'ADMIN' or find_user(username)['role'] == 'SELLER'):
            update.message.reply_text(
                "Welcome to shop management dashboard",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return SHOP_ACTION

    except (TypeError):
        update.message.reply_text(
            """You are not a registered seller or an admin. You do not have permission to access.
                """)
        done(update, context)
    except Exception as e:
        print(e)
        done(update, context)

    
def add_shop_item(update,context):
    update.message.reply_text(
            'What is the name of the new item?'
                )
    return GET_CREDITS

def input_item_credits(update,context):
    text = update.message.text
    context.user_data['item_name'] = text
    update.message.reply_text(
            'How many credits does it cost?'
    )
    return ADD_ITEM

def handle_item(update,context):
    credits = int(update.message.text)
    username = update.message.chat.username
    add_to_shop(username,context.user_data['item_name'],credits)
    update.message.reply_text(
             username + " has added " + context.user_data['item_name'] + " into his/her shop"
    )
    del context.user_data['item_name']
    return ConversationHandler.END

def delete_shop_item(update,context):
    update.message.reply_text(
            'Which item would you like to delete?'
                )
    return DELETE_ITEM

def handle_delete(update,context):
    text = update.message.text
    username = update.message.chat.username
    delete_item(username,text)
    update.message.reply_text(
        text + ' has been deleted from the shop')
    return ConversationHandler.END

def view_menu(update,context):
    username = update.message.chat.username
    menu = get_menu(username)
    for item in menu:
        update.message.reply_text(item)
    return ConversationHandler.END
    

def handle_exit_to_main(update, context):
    main.start(update, context)
    return ConversationHandler.END


# Database operations

def find_user(username):
    return altDB.Users.find_one({'username': username})

def add_to_shop(username,item,credits):
    items = altDB.Inventory.find_one({'username':username})['items']
    items.append({'item': item, 'price': credits})
    return altDB.Inventory.update(
        {'username': username},
        {'$set':
            {
                'items': items
            }
         }
    )

def delete_item(username,item_name):
    return altDB.Inventory.update_one(
    { 'username' : username},
    { '$pull': { 'items': { 'item': item_name } }})

def get_menu(username):
    items = altDB.Inventory.find_one({'username':username})['items']
    itemList = []
    for i in items:
        itemList.append(i['item']+ " , " + str(i['price']))
    return itemList

    """
    Conversation handler
    """


shop_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(
        r'Shop Management'), handle_shop_menu)],
    states={
        SHOP_ACTION: [MessageHandler(Filters.regex('^Add Item'),
                                     add_shop_item),
                      MessageHandler(Filters.regex('^Delete Item'),
                                      delete_shop_item),
                      MessageHandler(Filters.regex('^View My Store Items'),
                                      view_menu),
                      MessageHandler(Filters.regex('^Back to Menu$'),
                                     handle_exit_to_main)
                      ],

        GET_CREDITS: [MessageHandler(Filters.text,
                                        input_item_credits)
                    ],

        ADD_ITEM: [MessageHandler(Filters.text,
                                    handle_item),
                     ],
        
        DELETE_ITEM: [MessageHandler(Filters.text,
                                    handle_delete),
                     ],
        # userCONFIRMATION: [MessageHandler(Filters.regex('^CONFIRM$'),
        #                                   handle_confirmation),
        #                    MessageHandler(Filters.regex('^CANCEL$'),
        #                                   handle_exit_to_main)
        #                    ],

    },

    fallbacks=[MessageHandler(Filters.regex('^/done$'), handle_exit_to_main)],
)


#TESTING
# items = altDB.Inventory.find_one({'username':'Kaibing'})['items']
# itemList = []
# for i in items:
#     itemList.append(i['item']+ " , " + str(i['price']))
# print(itemList)
# items.append({'item': 'Cheese pizza', 'price': 10})
# print(items)
#id_code = altDB.Inventory.find_one({'username':'Kaibing'})['_id']
# altDB.Inventory.update_one(
#     { 'username' : 'Kaibing'},
#     { '$pull': { 'items': { 'item': "Hawaiian Pizza" } }})