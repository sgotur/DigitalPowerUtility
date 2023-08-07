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

# Make sure your region is correct.
# Make sure to handle exceptions if you are using the snippets in your projects.

import sys
import ssl
import json
import time
import random
import argparse
import os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

meters = [
            'Customer_Meter_1',
            'Customer_Meter_2',
            'Customer_Meter_3',
            'Customer_Meter_4',
            'Customer_Meter_5',
            'Customer_Meter_6',
            'Customer_Meter_7',
            'Customer_Meter_8',
            'Customer_Meter_9',
            'Customer_Meter_10',
            'Customer_Meter_11'
            ]

measure_data= dict()

# Get the AWS IoT Core endpoint url.
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--endpoint', type=str, required=True, help='AWS IoT Core endpoint url that AWSIoTMQTTClient connects to.')
args = vars(parser.parse_args())
endpoint = args['endpoint']

# Get the current directory path.
script_path = os.path.dirname(os.path.realpath(__file__))
print(script_path)

# Setup our MQTT client and security certificates.
# Make sure your certificate names match what you downloaded from AWS IoT.
mqttc = AWSIoTMQTTClient("DPU_Meter_Simulator")
mqttc.configureEndpoint(endpoint, 8883)
mqttc.configureCredentials(script_path + "/rootCA.pem", script_path + "/privateKey.pem", script_path + "/certificate.pem")

#Function to encode a payload into JSON.
def json_encode(string):
        return json.dumps(string)

# Function to return a string from a random array
def random_meter_id():
    meter_id = random.choice(meters)
    return meter_id

# Random floating point generator
def random_float_gen(initialValue, endValue, deimalPlace):
     return round(random.uniform(initialValue,endValue),deimalPlace)


# Function to create random float value for all the measure values. The range is based on real world examples.
def generate_measure_data():
     measure_data['voltage']=random_float_gen(280.1,289.9,2)
     measure_data['rssi']=random_float_gen(-49,-56,0)
     measure_data['current']=random_float_gen(45,80,0)
     measure_data['pf']=random_float_gen(0.80,1,2)
     

# This sends our message to the AWS IoT core using the specified topic.

def send():
    current_time = int(time.time() * 1000)
    for meter in meters:
       generate_measure_data()
       for k in measure_data:
            payload ={
            'meter_id':meter,
            k:measure_data[k],
            'time': current_time
            }
            mqttc.json_encode=json_encode        
            payload_json = mqttc.json_encode(payload)
            mqttc.publish("dpu/readings", payload_json, 0)
            print("Message published for {0} with payload {1}".format(meter, payload))
            time.sleep(3)
    print("Message published for all devices.")


def main():
    # Connect to the AWS IoT Core.
    mqttc.connect()
    print("Connected to AWS IoT Core.")
    # To check and see if your message was published to the message broker go to the MQTT Client and subscribe to the iot topic
    # and you should see your JSON Payload

    # Loop until terminated
    while True:
        send()
        time.sleep(5)
        
    mqttc.disconnect()

if __name__ == "__main__":
     main()
