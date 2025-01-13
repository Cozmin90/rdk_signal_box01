import tkinter as tk
import time
import serial
from robolink import Robolink  # Ensure this is imported correctly
from datetime import datetime  # Import datetime module for formatting the timestamp

# Initialize RoboDK and serial communication
RDK = Robolink()
ser = serial.Serial('COM4', 115200)

# Keep track of previous sensor values
prev_sensor1_value = None
prev_sensor2_value = None

# Log file setup
log_file = "D:/UPB/2024_2025_SEM_1/Articole/01_RoboDK signal Box/documente_articol_v1/latency_log.txt"

# Function to log latency and timestamp
def log_latency(latency, timestamp):
    # Convert timestamp to a readable format
    formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
    with open(log_file, "a") as file:
        file.write(f"{formatted_time}, {latency:.6f} ms\n")

# Function to handle executing RoboDK programs and updating the UI label
def execute_program_and_update_label(program_name, label):
    RDK.RunProgram(program_name)
    if program_name == "SET_IO1_0":
        label["text"] = "Sensor 1 Value: 0"
        label["bg"] = "yellow"
    elif program_name == "SET_IO1_1":
        label["text"] = "Sensor 1 Value: 1"
        label["bg"] = "green"
    elif program_name == "SET_IO2_0":
        label["text"] = "Sensor 2 Value: 0"
        label["bg"] = "yellow"
    elif program_name == "SET_IO2_1":
        label["text"] = "Sensor 2 Value: 1"
        label["bg"] = "green"

# Function to continuously read data from Arduino and update the UI
def read_arduino_data():
    global prev_sensor1_value, prev_sensor2_value
    while True:
        try:
            # Flush the serial buffer if it's too full
            if ser.in_waiting > 100:
                ser.reset_input_buffer()

            # Start measuring time when data is read
            start_time_pc = time.perf_counter()

            # Read data from Arduino
            if ser.in_waiting > 0:
                data = ser.readline().decode().strip()

                # Split the data into sensor identifier, value, and timestamp
                sensor, value, arduino_timestamp = data.split('_')
                arduino_timestamp = float(arduino_timestamp)

                # Check the current mode (manual/automatic)
                if current_mode.get() == 1:  # Only process Arduino data in automatic mode
                    # Calculate processing time
                    processing_time = (time.perf_counter() - start_time_pc) * 1000  # Convert to ms

                    # Handle IO1 (sensor 1)
                    if sensor == "IO1" and value != prev_sensor1_value:
                        prev_sensor1_value = value
                        execute_program_and_update_label(f"SET_IO1_{value}", label_signal_s1)
                        print(f"Arduino-to-Python processing time: {processing_time:.6f} ms")

                    # Handle IO2 (sensor 2)
                    elif sensor == "IO2" and value != prev_sensor2_value:
                        prev_sensor2_value = value
                        execute_program_and_update_label(f"SET_IO2_{value}", label_signal_s2)
                        print(f"Arduino-to-Python processing time: {processing_time:.6f} ms")

                    # Handle Photodiode (PD) sensor
                    elif sensor == "PD":
                        label_signal_pd["text"] = f"Photodiode Value: {value}"
                        RDK.setParam('Photodiode', value)

                    # End measuring time after running the RoboDK program
                    end_time_pc = time.perf_counter()
                    end_to_end_latency = (end_time_pc - start_time_pc) * 1000  # Convert to ms
                    timestamp = time.time()  # Get the current time in seconds
                    print(f"End-to-End Latency: {end_to_end_latency:.6f} ms")

                     # Log the end-to-end latency and timestamp
                    log_latency(end_to_end_latency, timestamp)

            # Small delay to avoid overwhelming the buffer
            time.sleep(0.01)

        except Exception as e:
            print(f"Error reading Arduino data: {e}")

# Function to handle mode change in the UI (manual/automatic mode)
def change_mode():
    if current_mode.get() == 0:
        label_mode.config(text="Mode: Manual")
        for button in buttons_manual.values():
            button.config(state=tk.NORMAL)
    else:
        label_mode.config(text="Mode: Automatic")
        for button in buttons_manual.values():
            button.config(state=tk.DISABLED)

# Create the main tkinter window
root = tk.Tk()
root.title("RoboDK Control")

# Create Tkinter variable for mode selection
current_mode = tk.IntVar()
current_mode.set(0)  # Initialize mode as manual

# Create labels to display signal values
label_signal_s1 = tk.Label(root, text="Sensor 1 Value: 0", bg="yellow")
label_signal_s1.pack()

label_signal_s2 = tk.Label(root, text="Sensor 2 Value: 0", bg="yellow")
label_signal_s2.pack()

label_signal_pd = tk.Label(root, text="Photodiode Value: 0", bg="yellow")
label_signal_pd.pack()

# Create a label to display the current mode
label_mode = tk.Label(root, text="Mode: Manual")
label_mode.pack()

# Create buttons for program execution in manual mode
buttons_manual = {}
program_names = ["SET_IO1_0", "SET_IO1_1", "SET_IO2_0", "SET_IO2_1"]

for program_name in program_names:
    buttons_manual[program_name] = tk.Button(root, text=program_name,
                                             command=lambda name=program_name: execute_program_and_update_label(name, label_signal_s1 if "IO1" in name else label_signal_s2))
    buttons_manual[program_name].pack()

# Create radio buttons for mode selection
radio_manual = tk.Radiobutton(root, text="Manual", variable=current_mode, value=0, command=change_mode)
radio_manual.pack()

radio_auto = tk.Radiobutton(root, text="Automatic", variable=current_mode, value=1, command=change_mode)
radio_auto.pack()

# Start a thread to continuously read data from Arduino
import threading
arduino_thread = threading.Thread(target=read_arduino_data)
arduino_thread.daemon = True
arduino_thread.start()

# Start the tkinter main loop
root.mainloop()

