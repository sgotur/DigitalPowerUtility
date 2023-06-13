#!/usr/bin/python

# MIT No Attribution
#
# Copyright 2022, Amazon Web Services
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Lab 1 - Setting up.
# Make sure your host and region are correct.

import sys
import ssl
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import random

meters = ["Customer_Meter_1", "Customer_Meter_2", "Customer_Meter_3", "Customer_Meter_4", "Customer_Meter_5", "Customer_Meter_6", "Customer_Meter_7", "Customer_Meter_8", "Customer_Meter_9", "Customer_Meter_10", "Customer_Meter_11"]

#Setup our MQTT client and security certificates
#Make sure your certificate names match what you downloaded from AWS IoT

mqttc = AWSIoTMQTTClient("DWM_Device")

# IoT core is created in Sydney
mqttc.configureEndpoint("aolb19ki9crxp-ats.iot.us-east-2.amazonaws.com", 8883)
mqttc.configureCredentials("./rootCA.pem","./privateKey.pem","./certificate.pem")

#Function to encode a payload into JSON
def json_encode(string):
        return json.dumps(string)

#write a function to create random float value between 19.20 to 33.24
def random_measure_value_float():
    return round(random.uniform(19.20,33.24),2)

#create a function to return a string from a random array
def random_meter_id():
    meter_id = random.choice(meters)
    return meter_id


#This sends our test message to the iot topic
def send():
    current_time = int(time.time() * 1000)
    for meter in meters:
        measureValue=random_measure_value_float()
        payload ={
        "meter_id": meter,
        "measure_value": measureValue,
        "time": current_time
        }

        mqttc.json_encode=json_encode
        
        #Encoding into JSON
        payload_json = mqttc.json_encode(payload)
        mqttc.publish("dpu/readings", payload_json, 0)
        print("Message published for {0} with payload {1}".format(meter, payload))
        time.sleep(3)
    print("Message published for all devices.")


#Connect to the gateway
mqttc.connect()
print("Connected")

#Loop until terminated
while True:
    send()
    time.sleep(5)

mqttc.disconnect()
#To check and see if your message was published to the message broker go to the MQTT Client and subscribe to the iot topic and you should see your JSON Payload