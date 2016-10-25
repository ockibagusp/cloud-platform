from __future__ import unicode_literals

from django.db import models
from nodes.models import Nodes
from sensors.models import Sensors


class Subscriptions(models.Model):
    node = models.ForeignKey(Nodes)
    sensor = models.ForeignKey(Sensors)
    data = models.CharField(max_length=128)
    timestamp = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.node.label + '_' + self.sensor.label + '@' + str(self.timestamp)

    class Meta:
        ordering = ('node', 'sensor', '-timestamp')
