import pymongo
# Your Telegram bot access key
BOT_ACCESS_KEY = '1202721044:AAGImDDtuW6IIZZVMxm6-65IzJjWFZfngOA'

##Connect to mongodb
client = pymongo.MongoClient("""mongodb+srv://Admin:admin123@cluster0-phjwg.mongodb.net/<dbname>?retryWrites=true&w=majority""")
database = client['Cluster0']