import socket
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Server settings
HOST = "127.0.0.1"
PORT_SENSOR = 4444      # Port for sensor data connection
PORT_ALERT = 5555       # Port for alert/command connection
BUFFER_SIZE = 1024

TEMP_THRESHOLD = 35    # Temperature threshold for alert
CO_THRESHOLD = 20       # CO level threshold for alert

# Data storage for live plotting
sensor_data = {"time": [], "temperature": [], "co": [], "alert": []}

# Create figure for live plots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

# First plot: Sensor Readings
ax1.set_xlabel("Time")
ax1.set_ylabel("Value")
ax1.set_title("Sensor Readings")
line_temp, = ax1.plot([], [], label="Temperature (°C)", color='r')
line_co, = ax1.plot([], [], label="CO Level", color='b')
ax1.legend()

# Second plot: Alert Output
ax2.set_xlabel("Time")
ax2.set_ylabel("Alert")
ax2.set_title("Alert Status (1 = Alert, 0 = Normal)")
line_alert, = ax2.plot([], [], label="Alert Status", color='g')
ax2.set_yticks([0, 1])
ax2.legend()

def update_plot(frame):
    """Update the live plot with the latest sensor data."""
    if sensor_data["time"]:
        ax1.clear()
        ax1.plot(sensor_data["time"], sensor_data["temperature"], label="Temperature (°C)", color='r')
        ax1.plot(sensor_data["time"], sensor_data["co"], label="CO Level", color='b')
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Value")
        ax1.set_title("Sensor Readings")
        ax1.legend()
        
        ax2.clear()
        ax2.plot(sensor_data["time"], sensor_data["alert"], label="Alert Status", color='g')
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Alert")
        ax2.set_title("Alert Status (1 = Alert, 0 = Normal)")
        ax2.set_yticks([0, 1])
        ax2.legend()
    return ax1, ax2

# Setup the animation (updates every 500ms)
ani = FuncAnimation(fig, update_plot, interval=500)

def send_alert(alert_status):
    """Send alert status to connected clients."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT_ALERT))
        server_socket.listen(1)
        print("Alert Server listening on port 5555")

        conn, addr = server_socket.accept()
        with conn:
            print(f"Connection established with {addr}")
            conn.sendall(b'1' if alert_status else b'0')
            time.sleep(1)

def start_server():
    """Set up server to receive sensor data and send alerts."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sensor_socket:
        sensor_socket.bind((HOST, PORT_SENSOR))
        sensor_socket.listen(1)
        print(f"Sensor Server listening on {HOST}:{PORT_SENSOR}")

        conn, addr = sensor_socket.accept()
        print(f"Sensor client connected from {addr}")

        while True:
            try:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                decoded = data.decode('utf-8')
                print(f"Received sensor data: {decoded}")

                parts = decoded.split(',')
                if len(parts) >= 3:
                    timestamp = float(parts[0])
                    temperature = float(parts[1])
                    co_level = float(parts[2])
                    print(f"Timestamp: {timestamp}, Temperature: {temperature}, CO Level: {co_level}")

                    # Determine alert condition
                    alert_status = 1 if temperature > TEMP_THRESHOLD or co_level > CO_THRESHOLD else 0
                    print(f"Sending alert status: {alert_status}")
                    
                    # Store data for plotting
                    sensor_data["time"].append(timestamp)
                    sensor_data["temperature"].append(temperature)
                    sensor_data["co"].append(co_level)
                    sensor_data["alert"].append(alert_status)

                    # Send alert status
                    send_alert(alert_status)
                    
                    # Echo received sensor data back to client (optional)
                    conn.sendall(data)
                time.sleep(1)
            except ConnectionResetError:
                print("Connection closed by client.")
                break

# Start the server loop in a separate daemon thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# Display the live plots
plt.show()
