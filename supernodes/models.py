from __future__ import unicode_literals

from mongoengine.document import Document, EmbeddedDocument
from mongoengine import StringField, FloatField, ReferenceField, EmbeddedDocumentField, \
    EmbeddedDocumentListField, CASCADE
from sensors.models import Sensors
from users.models import User


class Coordinates(EmbeddedDocument):
    lat = FloatField(required=True, null=False)
    long = FloatField(required=True, null=False)

    def __unicode__(self):
        return str([self.lat, self.long])


class Supernodes(Document):
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    label = StringField(max_length=28)
    secretkey = StringField(required=True, max_length=32)
    description = StringField(max_length=140, required=False)
    sensors = EmbeddedDocumentListField(document_type=Sensors)
    coordinates = EmbeddedDocumentField(document_type=Coordinates, required=False)

    def __unicode__(self):
        return self.label
