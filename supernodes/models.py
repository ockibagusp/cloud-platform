from __future__ import unicode_literals

from mongoengine.document import Document
from mongoengine import StringField, ReferenceField, EmbeddedDocumentListField, CASCADE
from sensors.models import Sensors
from users.models import User


class Supernodes(Document):
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    label = StringField(max_length=28)
    secretkey = StringField(required=True, max_length=32)
    description = StringField(max_length=140, required=False)
    sensors = EmbeddedDocumentListField(document_type=Sensors)

    def __unicode__(self):
        return self.label
