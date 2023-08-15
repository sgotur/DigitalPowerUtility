import pandas as pd
import json
import time
import datetime
import argparse
import os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Get the script parameters: a) AWS IoT Core endpoint url. b) publish option: customer or harmonics data
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--endpoint', type=str, required=True, help='AWS IoT Core endpoint url that AWSIoTMQTTClient connects to.')
parser.add_argument('-o', '--option', type=str, required=False, default='ALL', help='CUSTOMER: publishing customer data  HARMONICS: publishing harmonics data')
args = vars(parser.parse_args())
endpoint = args['endpoint']
option = args['option']

# Get the current directory path.
script_path = os.path.dirname(os.path.realpath(__file__))
mqttc_port = 8883
sleep_interval = 1  # second

# Setup our MQTT client and security certificates.
# Make sure your certificate names match what you downloaded from AWS IoT.
mqttc = AWSIoTMQTTClient("PQ_Meter_Simulator")
mqttc.configureEndpoint(endpoint, mqttc_port)
mqttc.configureCredentials(script_path + "/certs/rootCA.pem", script_path + "/certs/privateKey.pem",
                                script_path + "/certs/certificate.pem")

# Function to encode a payload into JSON.
def json_encode(string):
    return json.dumps(string)

# publish customer multi measure data: kwh, voltage, rssi, and pf
def publish_customer_data(topic, meterid, timestamp, uom, value):
    payload = {
            'meter_id': meterid,
             uom: value,
            'time': timestamp
    }
    mqttc.json_encode = json_encode
    payload_json = mqttc.json_encode(payload)
    mqttc.publish(topic, payload_json, 0)
    print("Message published for {0} with payload {1}".format(meterid, payload))

#publish harmonics meter data
def publish_harmonics_data(topic, timestamp, meter_id, value):
    payload = {
            'harmonic_meter_series_id':meter_id,
            'harmonics_value': value,
            'time': timestamp
    }
    mqttc.json_encode = json_encode
    payload_json = mqttc.json_encode(payload)
    mqttc.publish(topic, payload_json, 0)
    print("Message published for {0} with payload {1}".format(meter_id, payload))

#publish customer or harmonics meter data based on user option
def mqtt_publish_data():
    try:
        mqttc.connect()
        if option == 'CUSTOMER':
           read_and_publish_customer_meter_data()
        elif option == 'HARMONICS':
          read_and_publish_harmonics_data()
        elif option == 'ALL':
           read_and_publish_customer_meter_data()
           read_and_publish_harmonics_data()
        else:
           print("Wrong Option {0} must be: CUSTOMER or HARMINICS".format(option))
           exit(1)
    except Exception as e:
       print("MQTT Publish Error: " + str(e))

# Read and publish harmonics data.
def read_and_publish_harmonics_data():
    data_file = script_path + '/data/harmonics_metering_data.csv'
    df_meter_data = pd.read_csv(data_file)
    topic = 'dpu/harmonics-meter-data'
    for index, row in df_meter_data.iterrows():
        ctime = int(datetime.datetime.strptime(row['Read_Date_Timestamp_Local'], '%Y-%m-%dT%H:%M:%SZ').timestamp() * 1000)
        measure = row['harmonic_meter_series_id']
        value = row['value']
        publish_harmonics_data(topic, ctime, measure, value)
        time.sleep(sleep_interval)

# Read and publish customer meter data.
def read_and_publish_customer_meter_data():
    data_file = script_path + '/data/cust_metering_data.csv'
    topic = "dpu/customer-meter-data"
    df_meter_data = pd.read_csv(data_file)
    for index, row in df_meter_data.iterrows():
        meterid = row['meter_id']
        ctime = int(datetime.datetime.strptime(row['local_interval_datetime'], '%Y-%m-%dT%H:%M:%SZ').timestamp() * 1000)
        kwh = row['kwh']
        voltage = row['voltage']
        rssi = row['rssi']
        pf = row['pf']

        publish_customer_data(topic, meterid, ctime, 'kwh', kwh)
        publish_customer_data(topic, meterid, ctime, 'voltage', voltage)
        publish_customer_data(topic, meterid, ctime, 'rssi', rssi)
        publish_customer_data(topic, meterid, ctime, 'pf', pf)
        time.sleep(sleep_interval)

if __name__ == '__main__':
    print("Endpoint: {0} | Option: {1}".format(endpoint, option))
    mqtt_publish_data()