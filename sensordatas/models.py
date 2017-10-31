from mongoengine import Document, ObjectIdField
from mongoengine import ReferenceField, IntField, DateTimeField, CASCADE
from supernodes.models import Supernodes
from nodes.models import Nodes
import datetime


class Sensordatas(Document):
    supernode = ReferenceField(Supernodes,reverse_delete_rule=CASCADE)
    node = ReferenceField(Nodes, reverse_delete_rule=CASCADE)
    sensor = ObjectIdField(required=True)
    data = IntField()
    timestamp = DateTimeField(default=datetime.datetime.now())
