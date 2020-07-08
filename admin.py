import pymongo
from settings import database

#Function to create new user with specified amount of credits 
def create_new_user(username, credits): 
    database.users.insert_one({'user': username, 'credits': credits})

