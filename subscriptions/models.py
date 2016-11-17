from mongoengine import Document, ObjectIdField
from mongoengine import ReferenceField, StringField, DateTimeField, CASCADE
from nodes.models import Nodes
import datetime


class Subscriptions(Document):
    node = ReferenceField(Nodes, reverse_delete_rule=CASCADE)
    sensor = ObjectIdField(required=True)
    data = StringField(max_length=128)
    timestamp = DateTimeField(default=datetime.datetime.now())
