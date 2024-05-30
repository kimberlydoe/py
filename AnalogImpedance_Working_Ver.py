


"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-28

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import time
import sys
import numpy 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import os
import csv 
import threading

# creation of directory
output_dir = "Impedance_Data_Collection"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# Create the main window
root = tk.Tk()
fig, ax = plt.subplots()
root.title("Measurement Settings")

# tkinter application
frame = tk.Frame(root)

# Set the window size
root.geometry("630x400")
        
#How the impedance Anaylyzer actully works and makes Measurments
def makeMeasurement(steps, startFrequency, stopFrequency, reference, amplitude, makeMeasureTime):
    #Capture Current Date
    current_date = datetime.now()
    nowY = current_date.year
    nowD = current_date.day
    nowM = current_date.month
    now = str(nowM)+ '-' + str(nowD)+ '-' + str(nowY)
    voltage = 1
    makeMeasureTime = 6

    #Capture Current Time
    t = time.localtime()
    current_time = time.strftime("%H-%M-%S", t)

    if sys.platform.startswith("win"):
        dwf = cdll.LoadLibrary("dwf.dll")
    elif sys.platform.startswith("darwin"):
        dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    else:
        dwf = cdll.LoadLibrary("libdwf.so")

    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("DWF Version: "+str(version.value))

    hdwf = c_int()
    szerr = create_string_buffer(512)
    print("Opening first device\n")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == hdwfNone.value:
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        print("failed to open device")
        quit()

    # this option will enable dynamic adjustment of analog out settings like: frequency, amplitude...
    dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(3)) 

    sts = c_byte()

    # print("Reference: "+str(reference)+" Ohm  Frequency: "+str(startFrequency)+" Hz ... "+str(stopFrequency/1e3)+" kHz for nanofarad capacitors")
    dwf.FDwfAnalogImpedanceReset(hdwf)
    dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(8)) # 0 = W1-C1-DUT-C2-R-GND, 1 = W1-C1-R-C2-DUT-GND, 8 = AD IA adapter
    dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(reference)) # reference resistor value in Ohms
    dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(start_numeric_value)) # frequency in Hertz
    dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(amplitude)) # 1V amplitude = 2V peak2peak signal
    dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1)) # start
    time.sleep(2)

    rgHz = [0.0]*steps
    rgRs = [0.0]*steps
    rgXs = [0.0]*steps
    rgPhase = [0.0]*steps
    rgZ = [0.0]*steps
    rgRv = [0.0]*steps # real voltage
    rgIv = [0.0]*steps # imag voltage
    rgRc = [0.0]*steps # real current
    rgIc = [0.0]*steps # imag current

    for i in range(steps):
        hz = stop_numeric_value * pow(10.0, 1.0*(1.0*i/(steps-1)-1)*math.log10(stop_numeric_value/start_numeric_value)) # exponential frequency steps
        print("Step: "+str(i)+" "+str(hz)+"Hz")
        rgHz[i] = hz
        dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(hz)) # frequency in Hertz
        # if settle time is required for the DUT, wait and restart the acquisition
        # time.sleep(0.01) 
        # dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))
        while True:
            if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts)) == 0:
                dwf.FDwfGetLastErrorMsg(szerr)
                print(str(szerr.value))
                quit()
            if sts.value == 2:
                break
        resistance = c_double()
        reactance = c_double()
        phase = c_double()
        impedance = c_double()
        realVoltage = c_double()
        imagVoltage = c_double()
        realCurrent = c_double()
        imagCurrent = c_double()

        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceResistance, byref(resistance))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceReactance, byref(reactance))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedancePhase , byref(phase))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceImpedance, byref(impedance))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceVreal, byref(realVoltage))      
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceVimag, byref(imagVoltage)) 
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceIreal, byref(realCurrent))      
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceIimag, byref(imagCurrent))                
        # add other measurements here (impedance, impedanceVReal impedanceVImag, impedancelreal, impedancelimag)
        

        rgRs[i] = abs(resistance.value) # absolute value for logarithmic plot
        rgXs[i] = abs(reactance.value)
        rgPhase[i] = (phase.value * 180)/3.14159265358979
        rgZ[i] = abs(impedance.value)
        rgRv[i] = abs(realVoltage.value)
        rgIv[i] = abs(imagVoltage.value)
        rgRc[i] = abs(realCurrent.value)
        rgIc[i] = abs(imagCurrent.value)

        # graphs
        canvas = FigureCanvasTkAgg(fig, master= frame)
        canvas.get_tk_widget().pack()

        frame.grid(column= 0, row= 6)

        x = rgXs
        y = rgRs
        ax.plot()

        # plt.plot(rgHz, rgRs, rgHz, rgXs)
        # ax = plt.gca()
        # ax.set_xscale('log')
        # ax.set_yscale('log')
        # plt.show()

        now_time = now + '_at_' + current_time + '_data'

        data = pd.DataFrame({
                             'Frequency(Hz)': rgHz,'Impedance(Ohm)' : rgZ, 'Absolute Resistance(Ohm)': rgRs, 
                             'Absolute Reactance(Ohm)': rgXs, 'Phase(degrees)': rgPhase, 'Real Voltage(volts)': rgRv, 'Imaginary Voltage(volts)': rgIv, 
                              'Real Current(amps)': rgRc, 'Imaginary Current(amps)': rgIc })

        # Save the DataFrame to a CSV file
        csv_filename = os.path.join(output_dir, f"Impedance_Data_{now}_{current_time}.csv")
        data.to_csv(csv_filename, index=False)
        
        for iCh in range(2):
            warn = c_int()
            dwf.FDwfAnalogImpedanceStatusWarning(hdwf, c_int(iCh), byref(warn))
            if warn.value:
                dOff = c_double()
                dRng = c_double()
                dwf.FDwfAnalogInChannelOffsetGet(hdwf, c_int(iCh), byref(dOff))
                dwf.FDwfAnalogInChannelRangeGet(hdwf, c_int(iCh), byref(dRng))
                if warn.value & 1:
                    print("Out of range on Channel "+str(iCh+1)+" <= "+str(dOff.value - dRng.value/2)+"V")
                if warn.value & 2:
                    print("Out of range on Channel "+str(iCh+1)+" >= "+str(dOff.value + dRng.value/2)+"V")

    dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(0)) # stop
    dwf.FDwfDeviceClose(hdwf)

    print(f"Data saved to {csv_filename}")

    
#Extracts Steps value from GUI
def update_steps(*args):
    global steps_int
    try:
        # Convert the entry to an integer
        steps_int = int(steps.get())
        if steps_int < 0:
            raise ValueError("Steps cannot be negative.")
        print("Updated Steps to:", steps_int)

    except ValueError as e:
        print("Invalid input for steps. Please enter an integer")

# Dictionary for frequency values
frequency_dict = {
    "1 Hz": 1,
    "10 Hz": 10,
    "100 Hz": 100,
    "1 kHz": 1000,
    "10 kHz": 10000,
    "100 kHz": 100000,
    "1 MHz": 1000000,
    "10 MHz": 10000000,
    "15 MHz": 15000000
}

startFrequency = None
stopFrequency = None 
amplitude = None
reference = None

def on_select_start(event):
    global startFrequency
    global start_numeric_value
    startFrequency = startF_dropdown.get()
    start_numeric_value = frequency_dict[startFrequency]
    print(f"Selected: {startFrequency}, Numeric Value: {start_numeric_value}")

    return start_numeric_value

# Function to handle selection for stop frequency
def on_select_stop(event):
    global stopFrequency
    global stop_numeric_value
    stopFrequency = stopF_dropdown.get()
    stop_numeric_value = frequency_dict[stopFrequency]
    print(f"Selected: {stopFrequency}, Numeric Value: {stop_numeric_value}")

    return stop_numeric_value

# Dictionary for amplitude values
amplitude_dict = {
        "2 V" : 2,
        "1 V" : 1,
        "500 mV" : 0.5,
        "200 mV" : 0.2,
        "100 mV" : 0.1,
        "50 mV" : 0.05,
        "20 mV" : 0.02,
        "10 mV" : 0.01,
        "5 mV" : 0.005,
        "0 V" : 0
}

# Function to handle selection for amplitude
def on_select_amp(event):
    global amplitude
    global amplitude_numeric_value
    amplitude = amplitude_dropdown.get()
    amplitude_numeric_value = amplitude_dict[amplitude]
    print(f"Selected: {amplitude}, Numeric Value: {amplitude_numeric_value}")

    return amplitude_numeric_value

# Dictionary for resistance values
reference_dict = {
    "1 MΩ" : 1000000,
    "100 kΩ" : 100000,
    "10 kΩ" : 10000,
    "1 kΩ" : 1000,
    "100 Ω" : 100,
    "10 Ω" : 10
}

# Function to handle selection for resistance
def on_select_res(event):
    global reference
    global reference_numeric_value
    reference = resistance_dropdown.get()
    reference_numeric_value = reference_dict[reference]
    print(f"Selected: {reference}, Numeric Value: {reference_numeric_value}")

    return reference_numeric_value


# Function to start the measurement
def measure():
    global startFrequency, stopFrequency, amplitude, reference
    # Update global variables with the selected values
    steps = int(steps_entry.get())
    startFrequency = on_select_start(startFrequency)
    stopFrequency = on_select_stop(stopFrequency)
    reference = on_select_res(reference)
    amplitude = on_select_amp(amplitude)
    measure_interval = float(measure_interval_entry.get())

    # Call the function to make the measurement
    threading.Thread(target=makeMeasurement(steps, startFrequency, stopFrequency, reference, amplitude, measure_interval)).start()

    # Reset progress bar
    pb['value'] = 0
    value_label['text'] = updateProgressLabel()

# Function to handle Start and Stop
def staart():
    print("Measurement started")

def stoop():
    print("Measurement stopped")

# Steps entry
tk.Label(root, text="Steps").grid(row=0, column=0)
steps = tk.StringVar(value="151")  # Default value
steps.trace_add("write", update_steps)  # Trace changes
steps_entry = ttk.Entry(root, textvariable=steps)
steps_entry.grid(row=1, column=0)

# Start Frequency entry
tk.Label(root, text="Start Frequency").grid(row=0, column=1)
startF_dropdown = ttk.Combobox(root, values=list(frequency_dict.keys()))
startF_dropdown.bind("<<ComboboxSelected>>", on_select_start)
startF_dropdown.grid(row=1, column=1)
startF_dropdown.current(list(frequency_dict.keys()).index("100 Hz"))  # Set default value to 1 kHz

# Stop Frequency entry
tk.Label(root, text="Stop Frequency").grid(row=0, column=2)
stopF_dropdown = ttk.Combobox(root, values=list(frequency_dict.keys()))
stopF_dropdown.bind("<<ComboboxSelected>>", on_select_stop)
stopF_dropdown.grid(row=1, column=2)
stopF_dropdown.current(list(frequency_dict.keys()).index("1 MHz"))  # Set default value to 1 MHz

# Amplitude entry
tk.Label(root, text="Amplitude").grid(row=2, column=0)
amplitude_dropdown = ttk.Combobox(root, values=list(amplitude_dict.keys()))
amplitude_dropdown.bind("<<ComboboxSelected>>", on_select_amp)
amplitude_dropdown.grid(row=3, column=0)
amplitude_dropdown.current(list(amplitude_dict.keys()).index("1 V"))  # Set default value to 1 MHz

# Reference resistance dropdown
tk.Label(root, text="Reference resistance").grid(row=2, column=1)
resistance_dropdown = ttk.Combobox(root, values=list(reference_dict.keys()))
resistance_dropdown.bind("<<ComboboxSelected>>", on_select_res)
resistance_dropdown.grid(row=3, column=1)
resistance_dropdown.current(list(reference_dict.keys()).index("1 kΩ")) # set default value to 1 kΩ

# Measurement interval entry
tk.Label(root, text="Measure once every _ hours").grid(row=2, column=2)
measure_interval_entry = ttk.Entry(root)
measure_interval_entry.grid(row=3, column=2)
measure_interval_entry.insert(0, "4")  # Default value

# progress bar text
def updateProgressLabel():
    return f"Current Progress: {pb['value']}%"

def progress():
    if pb['value'] < 100:
        pb['value'] += 20
        value_label['text'] = updateProgressLabel()
    # else:
    #     # showinfo(message='The progress completed!')

def stop():
    pb.stop()
    value_label['text'] = updateProgressLabel()

# progressbar
pb = ttk.Progressbar(
    root,
    orient='horizontal',
    mode='determinate',
    length=280
)
# place the progressbar
pb.grid(column=0, row=5, columnspan=2, padx=10, pady=20)

# label
value_label = ttk.Label(root, text=updateProgressLabel())
value_label.grid(column=0, row=7, columnspan=2)

# start button
start_button = ttk.Button(
    root,
    text='Start',
    command=measure
)
start_button.grid(column=0, row=6, padx=10, pady=10, sticky=tk.E)

stop_button = ttk.Button(
    root,
    text='Stop',
    command=stoop
)
stop_button.grid(column=1, row=6, padx=10, pady=10, sticky=tk.W)

# Run the application
root.mainloop()
