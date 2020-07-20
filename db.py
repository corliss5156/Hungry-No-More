from collections import OrderedDict
from pymongo import MongoClient

# Connect to mongodb
client = MongoClient(
    """mongodb+srv://Admin:admin123@cluster0-phjwg.mongodb.net/<dbname>?retryWrites=true&w=majority""")

"""
 Todo: integrate into main schema
 
"""
altDB = client['Alternative-Schema']

"""
User Schema
"""
userValidation = {"$jsonSchema":
                  {
                      "bsonType": "object",
                      "required": ["username", "role", "balance"],
                      "properties": {
                          "username": {
                              "bsonType": "string",
                              "description": "must be a string and is required"
                          },
                          "role": {
                              "enum": ["ADMIN", "CONSUMER", "SHOPS"],
                              "description": "can only be one of the enum values and is required"
                          },
                          "balance": {
                              "bsonType": "long",
                              "description": "credit balance in cents"
                          },
                      }
                  }
                  }


userConfig = OrderedDict([('collMod', 'Users'),
                          ('validator', userValidation),
                          ('validationLevel', 'moderate')])


"""
Transaction Schema
"""

transactionValidation = {"$jsonSchema":
                         {
                             "bsonType": "object",
                             "required": ["payer", "payee", "amount", "description", "date"],
                             "properties": {
                                 "payer": {
                                     "bsonType": ["objectId", "null"],
                                     "description": "Must be an objectID"
                                 },
                                 "payee": {
                                     "bsonType": "objectId",
                                     "description": "objectId of the receiver"
                                 },
                                 "amount": {
                                     "bsonType": "long",
                                     "description": "amount in cents"
                                 },
                                 "description": {
                                     "bsonType": "string",
                                     "description": "nature of transaction"
                                 },
                                 "date": {
                                     "bsonType": "timestamp",
                                     "description": "time of transaction"
                                 }
                             }
                         }
                         }


# transactionConfig = OrderedDict([('collMod', 'Transactions'),
#                                  ('validator', transactionValidation),
#                                  ('validationLevel', 'moderate')])
# altDB.command(userConfig)
# altDB.command(transactionConfig)
