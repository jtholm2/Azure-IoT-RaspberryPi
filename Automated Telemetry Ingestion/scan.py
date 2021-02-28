import os, json, time, re
import pandas as pd
from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = "{insert Azure IoT Hub connection string here}"

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

def formatData(fileToFormat):
    list = []
    with open(fileToFormat, mode='r') as csv_file:
        keys = csv_file.readline().strip().split(',')
        for line in csv_file:
            line = line.strip()
            row = re.split(r'(?!\s),(?!\s)',line)
            list.append(dict(zip(keys, row)))

    formattedCsv = pd.DataFrame(list)
    droppedDuplicates = formattedCsv.drop_duplicates(subset=[' BSSID', ' Latitude', ' Longitude'])
    return droppedDuplicates.to_json(orient='records')


def iothub_client_survey_scan():

    try:
        client = iothub_client_init()
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )

        while True:
            print('starting scan')
            os.system('screen -d -m sudo airodump-ng --gpsd -w testEndpointOutput --output-format logcsv wlan1mon')
            time.sleep(15)
            print('stopping scan')
            os.system('sudo pkill airodump-ng')
            jsonToSend = formatData('testEndpointOutput-01.log.csv')
            os.system('sudo rm testEndpointOutput-01.log.csv testEndpointOutput-01.gps')

            message = Message(jsonToSend)

            # Send the message.
            print( f'Sending message: {message}' )
            client.send_message(message)
            print ( "Message successfully sent" )
            time.sleep(1)

    except KeyboardInterrupt:
        print ( "IoTHubClient stopped" )

if __name__ == '__main__':
    print ( "IoT Hub RPI Wireless Scan" )
    print ( "Press Ctrl-C to exit" )
    iothub_client_survey_scan()
