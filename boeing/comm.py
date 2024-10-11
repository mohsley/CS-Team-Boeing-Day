import socket
import struct
import serial
import time

UDP_IP = "0.0.0.0"
UDP_PORT = 8888
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

def init_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}")
    return sock

def init_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow time for Arduino to reset
        print(f"Serial connection established on {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

def process_udp_data(data):
    try:
        num_floats = len(data) // 4
        format_string = f'{num_floats}f'
        angles = struct.unpack(format_string, data)
        angles_int = [int(angle) for angle in angles]
        return ','.join(map(str, angles_int))
    except struct.error as e:
        print(f"Error unpacking data: {e}")
        print(f"Received data length: {len(data)} bytes")
        return None

def send_to_arduino(serial_conn, data):
    serial_conn.write(f"{data}\n".encode())
    serial_conn.flush()
    print(f"Sent to Arduino: {data}")
    
    start_time = time.time()
    while time.time() - start_time < 1:  # 1-second timeout
        if serial_conn.in_waiting:
            response = serial_conn.readline().decode().strip()
            print(f"Arduino: {response}")
            if response == "READY":
                return True
        time.sleep(0.01)
    return False

def main():
    udp_socket = init_udp()
    serial_conn = init_serial()

    if not serial_conn:
        print("Failed to initialize serial connection. Exiting.")
        return

    try:
        while True:
            data, addr = udp_socket.recvfrom(1024)
            if len(data) > 0:
                print(f"Received data from {addr}")
                processed_data = process_udp_data(data)
                if processed_data:
                    if send_to_arduino(serial_conn, processed_data):
                        print("Arduino processed data successfully")
                    else:
                        print("Arduino did not respond in time")
                else:
                    print("Failed to process UDP data")
            
            # Check for any additional output from Arduino
            while serial_conn.in_waiting:
                arduino_output = serial_conn.readline().decode().strip()
                print(f"Arduino: {arduino_output}")

    except KeyboardInterrupt:
        print("Interrupted by user, shutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        udp_socket.close()
        serial_conn.close()
        print("Connections closed.")

if __name__ == "__main__":
    main()