from mongoengine.document import Document, EmbeddedDocument
from mongoengine import StringField, ReferenceField, EmbeddedDocumentListField, IntField, CASCADE, ObjectIdField
from sensors.models import Sensors
from users.models import User
# delete embeded -> Nodes.objects(label="FILKOM_1").update_one(pull__sensors__label="HUMIDITY")


class Nodes(Document):
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    label = StringField(max_length=28, unique=True, sparse=True)
    secretkey = StringField(max_length=16)
    subsperday = IntField(default=0)
    subsperdayremain = IntField(default=0)
    sensors = EmbeddedDocumentListField(document_type=Sensors)

    meta = {
        'indexes': [
            {
                'fields': ['-label'],
                'unique': True,
                'types': False
             },
        ],
    }
