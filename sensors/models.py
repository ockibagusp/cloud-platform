from __future__ import unicode_literals
import bson
from mongoengine import StringField, ObjectIdField
from mongoengine.document import EmbeddedDocument


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
