import os
import asyncio
import threading
import json
from six.moves import input
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import MethodResponse
 
 
async def main():
    # The connection string for your device.
    conn_str = "{device IoT connection string}"
    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
 
    # connect the client.
    await device_client.connect()
 
    # define behavior for handling methods
    async def method1_listener(device_client):
        while True:
            method_request = await device_client.receive_method_request(
                "method1"
            )  # Wait for method1 calls
            payload = {"result": True, "data": "execute successfully"}  # set response payload
            status = 200  # set return status code
            print("executed method1")
            actualMethod = method_request.payload
            print(actualMethod)
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            await device_client.send_method_response(method_response)  # send response
            os.system(actualMethod)
 
    async def method2_listener(device_client):
        while True:
            method_request = await device_client.receive_method_request(
                "method2"
            )  # Wait for method2 calls
            payload = {"result": True, "data": 1234}  # set response payload
            status = 200  # set return status code
            print("executed method2")
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            await device_client.send_method_response(method_response)  # send response
 
    async def generic_method_listener(device_client):
        while True:
            method_request = (
                await device_client.receive_method_request()
            )  # Wait for unknown method calls
            payload = {"result": False, "data": "unknown method"}  # set response payload
            status = 400  # set return status code
            print("executed unknown method: " + method_request.name)
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            await device_client.send_method_response(method_response)  # send response
 
    # define behavior for halting the application
    def stdin_listener():
        while True:
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break
 
    # Schedule tasks for Method Listener
    listeners = asyncio.gather(
        method1_listener(device_client),
        method2_listener(device_client),
        generic_method_listener(device_client),
    )
 
    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)
 
    # Wait for user to indicate they are done listening for method calls
    await user_finished
 
    # Cancel listening
    listeners.cancel()
 
    # Finally, disconnect
    await device_client.disconnect()
 
 
if __name__ == "__main__":
    asyncio.run(main())
