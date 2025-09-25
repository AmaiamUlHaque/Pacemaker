import json
import hashlib
import os
from typing import Optional, Dict, List

#Path to the file used to store users, constant
USER_FILE = os.path.join(os.path.dirname(__file__)),"..","storage", "users.json"

#max number of users allow in the local system
MAX_USERS = 10

#note on notation, functions starting with "_" are internal and not a part of the external library API

def _loadUsers() -> Dict[str, str]:
    """
    Load user from JSON file. Returns dict{username: password_hash}
    """
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def _saveUsers(users: Dict[str, str]) -> None:
    """
    Save the user data into JSON File.
    """
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def _hashPassword(password: str) -> str:
    """
    basic encrypting of passwords using SHA256. returns the hashed version. 
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(username : str, password : str) -> bool:
    """
    Register a new user. Returns true if successful false if:
    - username is taken
    - user_limit exceeeded
    """
    users = _loadUsers()
    
    if username in users:
        return False
    if len(users) >= MAX_USERS:
        return False

    users[username] = _hashPassword(password)
    _saveUsers(users)
    return True

def authenticate_user(username: str, password: str) -> bool:
    """
    Check if username exists and password is correct
    """
    users = _loadUsers()
    
    if username not in users:
        return False
    return users[username] == _hashPassword(password)

def list_users() -> List[str]:
    """
    give a list of the all the users currently stored
    """
    
    return list(_loadUsers().keys())

def remove_user(username: str) -> bool:
    """
    returns true if removed false if not found
    """
    
    users = _loadUsers()
    
    if username not in users:
        return False
    del users[username]
    _saveUsers(users)
    return True

def reset_users()->None:
    """
    clears out all the users from the json file
    """
    
    _saveUsers({})
    
    
    
    

