from __future__ import unicode_literals

from django.db import models
from nodes.models import Nodes


class Sensors(models.Model):
    nodes = models.ForeignKey(Nodes)
    label = models.CharField(max_length=28, unique=True)

    def __unicode__(self):
        return self.label

    class Meta:
        ordering = ('label',)


