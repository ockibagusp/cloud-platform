from mongoengine.document import Document
from mongoengine import StringField, EmailField, IntField


class User(Document):
    email = EmailField(required=True)
    username = StringField(min_length=4, max_length=16, unique=True, required=True)
    password = StringField(min_length=8, max_length=128, required=True)
    first_name = StringField(max_length=50, required=True)
    last_name = StringField(max_length=50, required=True)
    is_admin = IntField(default=0)

    meta = {
        'indexes': [
            {
                'fields': ['-username'],
                'unique': True
            },
        ],
    }