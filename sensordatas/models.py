from mongoengine import Document, ObjectIdField
from mongoengine import ReferenceField, FloatField, DateTimeField, CASCADE
from supernodes.models import Supernodes
from nodes.models import Nodes
import datetime


class Sensordatas(Document):
    supernode = ReferenceField(Supernodes, reverse_delete_rule=CASCADE)
    node = ReferenceField(Nodes, reverse_delete_rule=CASCADE, required=False, null=True)
    sensor = ObjectIdField(required=True)
    data = FloatField()
    timestamp = DateTimeField(default=datetime.datetime.now())
