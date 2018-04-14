# Import library
import paho.mqtt.client as mqtt
from models import *

# Koneksi ke DB
connect('agrihub')

# Inisiasi mqtt client
mqttc = mqtt.Client("subfull", clean_session=True)
mqttc.username_pw_set(username="s3rv3r", password="rahasia")


# Inisiasi callback function
def message_in(mqttc, obj, msg):
    item = json.loads(msg.payload)
    # print item
    for post in Nodes.objects:
        finish = False
        fail = True
        if post.label == item['node'] and post.subsperdayremain > 0:
            for x in post.sensors:
                remain = post.subsperdayremain
                for i in item['sensor']:
                    if x.label == i['label']:
                        store = Subscriptions(data=i['data'], sensor=x.id, node=post.id)
                        # remain = post.subsperdayremain
                        store.save()
                        remain = remain - 1
                        # post.update(subsperdayremain=remain-1)
                        print "stored >> " + item['node'] + " | " + i['label'] + " | " + i['data']
                        finish = True
                # fail = False
                # if fail == True :
                #     print "fail >> "+item['node']+" | "+i['label']+" | "+i['data']
                post.update(subsperdayremain=remain)
                if finish:
                    break
        if finish:
            break


def on_connect(client, userdata, flags, rc):
    m = "Connected flags " + str(flags) + "\nresult code " + str(rc) + "\nclient_id  " + str(client)
    print(m)


# Registrasi callback funtion
mqttc.on_message = message_in
mqttc.on_connect = on_connect

# Buat Koneksi ke broker
mqttc.connect("127.0.0.1", 1883)

# Subscribe dengan topik semua
mqttc.subscribe("#")
print("Server is running...")

# Looping forever
mqttc.loop_forever()
