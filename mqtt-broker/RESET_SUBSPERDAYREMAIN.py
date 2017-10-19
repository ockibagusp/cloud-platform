#!/usr/bin/python
import bson, datetime
from mongoengine import *
from models import *

connect('agrihub')

for post in Nodes.objects :
    post.update(subsperdayremain=post.subsperday)
