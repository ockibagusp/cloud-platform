from __future__ import unicode_literals

from django.db import models


class Nodes(models.Model):

    label = models.CharField(unique=True, max_length=28)
    secretkey = models.CharField(max_length=16)
    subsperday = models.IntegerField(default=0)
    subsperdayremain = models.IntegerField(default=0)

    def __unicode__(self):
        return self.label

    class Meta:
        ordering = ('label',)
