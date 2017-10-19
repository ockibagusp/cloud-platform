import json
import httplib
import random

from models.credentials import Credentials


class AgriHubAPI:
    def __init__(self):
        with open('settings.json') as json_settings:
            self.settings = json.load(json_settings)
        self.headers = {'Content-Type': 'application/json'}
        self.credential_model = Credentials()

    def createconnection(self):
        return httplib.HTTPConnection(self.settings.get('api_url'))

    def auth(self):
        conn = self.createconnection()
        data = json.dumps({
            "user": self.settings.get('user'),
            "label": self.settings.get('node')['label'],
            "secretkey": self.settings.get('node')['secretkey']
        })
        conn.request('POST', '/node-auth/', data, self.headers)
        res = conn.getresponse()
        if 200 == res.status:
            print 'AUTH: ok'
            res_data = json.loads(res.read())
            conn.close()
            self.credential_model.set(res_data.get('token'), res_data.get('node')['subsperdayremain'])
        else:  # 400
            conn.close()
            # TODO simpan error di log
            exit('AUTH: failure')

    def subscribe(self, testing=False):
        credential = self.credential_model.get()
        # if node has no remaining subs, then ignore it
        if 0 == credential[1]:
            return
        conn = self.createconnection()
        sensors = self.settings.get('node')['sensors']
        data_raw = {
            "user": self.settings.get('user'),
            "node": self.settings.get('node')['label'],
            "sensor": [],
            "testing": testing
        }

        for sensor in sensors:
            # TODO data should captured with sensor module
            data_raw.get('sensor').append({
                "label": sensor,
                "data": random.randint(100, 999)
            })

        self.headers.update({'Authorization': "JWT %s" % (credential[0])})
        conn.request('POST', '/subscriptions/', json.dumps(data_raw), self.headers)
        res = conn.getresponse()

        # sent new auth() when token is expired
        if 401 == res.status:
            print "Subs status: 401"
            print res.read()
            print "Renew token..."
            self.auth()
            self.subscribe()
        else:
            print "Subs status: 200 (ok)"
