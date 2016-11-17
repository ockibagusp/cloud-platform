from mongoengine.document import Document
from mongoengine import StringField, EmailField


class User(Document):
    email = EmailField()
    username = StringField(max_length=16)
    password = StringField(min_length=8, max_length=128)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
