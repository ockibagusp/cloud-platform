from mongoengine.document import Document
from mongoengine import StringField, ReferenceField, EmbeddedDocumentListField, IntField, CASCADE
from sensors.models import Sensors
from users.models import User
# delete embeded -> Nodes.objects(label="FILKOM_1").update_one(pull__sensors__label="HUMIDITY")


class Nodes(Document):
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    label = StringField(max_length=28)
    secretkey = StringField(required=True, max_length=16)
    is_public = IntField(default=0)
    subsperday = IntField(default=0)
    subsperdayremain = IntField(default=0)
    sensors = EmbeddedDocumentListField(document_type=Sensors)
