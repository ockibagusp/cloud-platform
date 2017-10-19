import bson, json, hashlib, datetime
from mongoengine import *


#Class untuk mongoengine
class Sensors(EmbeddedDocument):
    id = ObjectIdField(default=bson.objectid.ObjectId())
    label = StringField(max_length=28)

    meta = {
        'indexes': [
            {
                'fields': ['-label'],
                'unique': True,
                'types': False
            },
        ],
    }

    def __unicode__(self):
        return self.label


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



class Nodes(Document):
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    label = StringField(max_length=28)
    secretkey = StringField(required=True, max_length=16)
    is_public = IntField(default=0)
    subsperday = IntField(default=0)
    subsperdayremain = IntField(default=0)
    sensors = EmbeddedDocumentListField(document_type=Sensors)


class Subscriptions(Document):
    node = ReferenceField(Nodes, reverse_delete_rule=CASCADE)
    sensor = ObjectIdField(required=True)
    data = IntField()
    timestamp = DateTimeField(default=datetime.datetime.now())
