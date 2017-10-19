#Import library
import paho.mqtt.client as mqtt
import json, hashlib
from random import randint

#Inisiasi mqtt client
mqttc = mqtt.Client("ASDAAA", clean_session=False)
mqttc.username_pw_set(username="FILKOM_1",password="rahasia")


#Registrasi callback
#mqttc.on_connect = on_connect

#Buat Koneksi ke broker
mqttc.connect("127.0.0.1", 1883)

dict_data = {
            'node' : "FILKOM_1",
            'sensor' : [
            {'label' : "TEMP",'data' : str(randint(10,30))},
            {'label' : "TEMP",'data' : str(randint(10,30))}
            ]
            }

data = json.dumps(dict_data)
print data

#Publish message dengan topik tertentu
mqttc.publish("basukicahya/FILKOM_1", payload=data, qos=1, retain=False)
