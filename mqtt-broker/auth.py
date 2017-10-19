#!/usr/bin/python

import sys

import bottle

from bottle import response, request

from pymongo import MongoClient



client = MongoClient('localhost', 27017)

db = client['agrihub']

nodes = db['nodes']

user = db['user']



app = application = bottle.Bottle()



@app.route('/auth', method='POST')

def auth():

    response.content_type = 'text/plain'

    response.status = 403



    username = request.forms.get('username')

    password = request.forms.get('password')



    if username == "s3rv3r":

        response.status = 200

        return None



    for node in nodes.find({"label":username,"secretkey":password}):

        response.status = 200

        return None



    return None



@app.route('/superuser', method='POST')

def superuser():

    response.content_type = 'text/plain'

    response.status = 403



    username = request.forms.get('username')



    if username == 's3rv3r':

        response.status = 200





    return None





@app.route('/acl', method='POST')

def acl():

    response.content_type = 'text/plain'

    response.status = 403



    username = request.forms.get('username')

    topic    = request.forms.get('topic')

    # clientid = request.forms.get('clientid')

    # acc      = request.forms.get('acc') # 1 == SUB, 2 == PUB



    for node in nodes.find({"label":username}):

        userid = node['user']

        for users in user.find({"_id":userid}):

            if topic == users['username']+'/'+node['label']:

                response.status = 200

                return None



    return None



if __name__ == '__main__':



    bottle.debug(True)

    bottle.run(app,

        # server='python_server',

        host= "127.0.0.1",

        port= 8100)
