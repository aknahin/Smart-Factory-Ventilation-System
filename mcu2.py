from gpio import *
from time import *
from realtcp import *

serverIP = "127.0.0.1"
serverPort = 5555

client = RealTCPClient()
received_data = None

def onTCPConnectionChange(type):
    print("Connection changed: " + str(type))

def onTCPReceive(data):
    global received_data
    try:
        received_data = data.strip()  # Remove any unwanted whitespace or newlines
        print("Received:", received_data)
    except Exception as e:
        print("Error processing received data:", e)

def main():
    global received_data
    
    for pin in range(0, 4):
        pinMode(pin, INPUT)

    

    while True:
        client.onConnectionChange(onTCPConnectionChange)
        client.onReceive(onTCPReceive)
        client.connect(serverIP, serverPort)
        if received_data is not None:
            data = received_data
            received_data = None  # Reset after processing

            if data == "1":
                digitalWrite(0, HIGH)
                customWrite(1,'1')
                customWrite(2,'1')
                print("Pins set to HIGH")
            elif data == "0":
                digitalWrite(0, LOW)
                customWrite(1,'0')
                customWrite(2,'0')
                print("Pins set to LOW")
        else:
            print("Invalid data received:", received_data)

        delay(1000)

if __name__ == "__main__":
    main()
