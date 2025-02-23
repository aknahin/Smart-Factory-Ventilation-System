from gpio import *
from time import *
from realtcp import *

serverIP = "127.0.0.1"
serverPort = 4444

client = RealTCPClient()

def onTCPConnectionChange(type):
    print("connection changed: " + str(type))
    
def onTCPReceive(data):
    print("received: " + data)

def main():
    pinMode(0, OUT)
    coSensorPin = A0
    temperaturePin = A1
    pinMode(coSensorPin, INPUT)
    pinMode(temperaturePin, INPUT)
    client.onConnectionChange(onTCPConnectionChange)
    client.onReceive(onTCPReceive)
    client.connect(serverIP, serverPort)
    count = 0
    while True:
        temperature = analogRead(temperaturePin)
        temperature = (temperature / 1023.0) * 200 - 100
        coLaverl = analogRead(coSensorPin)
        CO_level = 2.62 * (coLaverl/1023.0) * 100
        print("Temperature:", temperature)
        print("CO:", coLaverl)
        count += 1
        if client.state() == 3:
            client.send(str(count) + "," + str(temperature) + "," + str(CO_level))
        customWrite(0, "T: " + str(temperature) + " C" + "\n" + "CO: " + str(CO_level))
        delay(1000)
        
if __name__ == "__main__":
    main()