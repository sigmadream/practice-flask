from user import User
from app import jwt

users = [
    User(1, "admin", "qwer1234"),
]
username_mapping = {u.name: u for u in users}
userid_mapping = {u.id: u for u in users}


@jwt.user_identity_loader
def identity(payload):
    user_id = payload["identity"]
    return userid_mapping.get(user_id, None)


def authenticate(username, password):
    user = username_mapping.get(username, None)
    if user and user.password == password:
        return user
