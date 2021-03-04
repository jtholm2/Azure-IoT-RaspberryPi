# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time, os, sys, asyncio, re
import pandas as pd
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

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

        
        # define behavior for receiving an input message on input1
        async def scan_start_ingest(module_client):
            while True:
                print('starting scan')
                os.system('screen -d -m sudo airodump-ng --gpsd -w testEndpointOutput --output-format logcsv wlan1mon')
                time.sleep(15)
                print('stopping scan')
                os.system('screen -d -m sudo pkill airodump-ng')
                jsonToSend = formatData('testEndpointOutput-01.log.csv')
                os.system('screen -d -m sudo rm testEndpointOutput-01.log.csv testEndpointOutput-01.gps')
                message = Message(jsonToSend)

                # Send the message.
                print( "Sending message" )
                await module_client.send_message_to_output(message, "output1")
                print ( "Message successfully sent" )
                time.sleep(1)

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)

        # Schedule task for C2D Listener
        listeners = asyncio.gather(scan_start_ingest(module_client))

        print ( "The sample is now waiting for messages. ")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()