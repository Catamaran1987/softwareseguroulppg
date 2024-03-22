from werkzeug.security import generate_password_hash, check_password_hash

users = {}


def add_user(username, password):
    if username in users:
        return False
    users[username] = generate_password_hash(password)
    print(f"Added user {username}.")
    return True


def check_user(username, password):
    if username in users and check_password_hash(users[username], password):
        return True
    return False
