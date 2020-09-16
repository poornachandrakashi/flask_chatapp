#all the logic for connecting the databases
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime
from user import User
from bson.objectid import ObjectId

client = MongoClient("mongodb+srv://test:poorna1999@cluster0.qqz3a.mongodb.net/test?retryWrites=true&w=majority")

#Find the database
chat_db=client.get_database('ChatDb')
users_collection = chat_db.get_collection("users")
rooms_collection =  chat_db.get_collection("rooms")
room_members_collection = chat_db.get_collection("room_members")


#Function to save the particular user
def save_user(username,email,password):
    password_hash=generate_password_hash(password)
    users_collection.insert_one({ '_id':username, 'email':email,'password':password_hash})


def get_room(room_id):
    rooms_collection.find_one({'_id':ObjectId(room_id)})


#To save a room
def save_room(room_name,created_by):
    room_id=rooms_collection.insert_one({'room_name':room_name,'created_by':created_by,'created_at':datetime.now()}).inserted_id
    
    #use the id to save the room admins
    add_room_member(room_id,room_name,created_by,created_by, is_room_admin=True)
    return room_id    
    
def add_room_member(room_id,room_name,username,added_by,is_room_admin=False):
    room_members_collection.insert_one({'_id':{'room_id':Object_id(room_id),'username': username},'room_name':room_name,'added_by':added_by,'added_at':datetime.now(),'is_room_admin':is_room_admin})
    
def add_room_members(room_id,room_name,usernames,added_by):
    room_members_collection.insert_many([{'_id':{'room_id':Object_id(room_id),'username': username},'room_name':room_name,'added_by':added_by,'added_at':datetime.now(),'is_room_admin':False} for username in usernames])

def get_user(username):
    user_data = users_collection.find_one({'_id': username})
    return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None

def get_room_members(root_id):
    room_members_collection.find({'_id.room_id': room_id})

def update_room(room_id,room_name):
    rooms_collection.update_one({'_id':{'$in':[{'room_id':room_id,'username':username} for username in usernames]}})
                                
                                
                                
def remove_room_members():
    room_members_collection.delete_many({'_id':{'$in':[{'room_id':room_id,'username':username} for username in usernames]}})

def get_rooms_for_user(username):
    room_members_collection.find({'_id.username':username})
    
    
def is_room_member(room_id,username):
    room_members_collection.count_documents({'_id':{'room_id':ObjectId(room_id),username:username}})
    
    
def is_room_admin(room_id,username):
    room_members_collection.count_documents({'_id':{'room_id':ObjectId(room_id),username:username},'is_room_admin':True})
    