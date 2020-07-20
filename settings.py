import pymongo
# Your Telegram bot access key
BOT_ACCESS_KEY = '1202721044:AAGImDDtuW6IIZZVMxm6-65IzJjWFZfngOA'
API_TOKEN = "1313316041:AAF7xePQg9tThG_lL-FfprCnOW6Ws2nlXZc"

# Connect to mongodb
client = pymongo.MongoClient(
    """mongodb+srv://Admin:admin123@cluster0-phjwg.mongodb.net/<dbname>?retryWrites=true&w=majority""")
database = client['Cluster0']

"""
 Todo: integrate into main schema
 
 altDB comes with 3 collections: Users, Transactions, Fund
"""
altDB = client['Alternative-Schema']
