from __future__ import unicode_literals

from mongoengine.document import Document
from mongoengine import StringField, ReferenceField, CASCADE
from users.models import User


class Supernodes(Document):
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    label = StringField(max_length=28)
    description = StringField(max_length=140, required=False)

    def __unicode__(self):
        return self.label
