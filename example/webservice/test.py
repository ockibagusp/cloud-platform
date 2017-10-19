from models.credentials import Credentials
from models.subs_schedule import SubsScedule
from utils.http import AgriHubAPI
import datetime

"""
Credentials Model -> pass
"""
creds = Credentials()
print "Credentials Model Test"
print "======================"
print "Set expired token"
creds.set(
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWJzcGVyZGF5IjoyMCwiaWQiOjEsImV4cCI6MTQ3ODA2NTQwNiwibGFiZWwiOiJGSUxLT01fMSJ9."
    "GV0JQ2Ii0hfipLMo7r1t-T3Sy1rE_1yujB9c75zFqDc",
    20
)
print "Get credentials data"
creds.get()

"""
SubsScedule Model -> pass
"""
subs = SubsScedule()
print "\nCredentials Model Test"
print "======================"
print "Create new subs date"
subs.create(
    datetime.time(0, 35)
)
print "Get all subs"
all_subs = subs.getall()
print all_subs
last = all_subs[-1][0]
print "Get last record id: %d" % last
print "Edit subs id=%d, set `date` to 12:50" % last
subs.edit(last, datetime.time(12, 50))
print "Get subs id=%d" % last
print subs.getbyid(last)
print "Deleting subs id=%d" % last
subs.delete(last)

"""
Http lib -> pass
"""
print "\nHttp lib Test"
print "======================"
api = AgriHubAPI()
print "Subs sensor data"
api.subscribe()
print "Auth test"
api.auth()
