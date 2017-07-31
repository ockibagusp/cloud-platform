from mongoengine import Document, ObjectIdField
from mongoengine import ReferenceField, IntField, DateTimeField, CASCADE
from nodes.models import Nodes
import datetime


class Sensordatas(Document):
    node = ReferenceField(Nodes, reverse_delete_rule=CASCADE)
    sensor = ObjectIdField(required=True)
    data = IntField()
    timestamp = DateTimeField(default=datetime.datetime.now())
