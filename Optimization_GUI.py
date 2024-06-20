import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import numpy as np
from pyswarms.single import GlobalBestPSO
import math
import matlab.engine

# Frequency values dictionary
frequency_values = {
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

freq_keys = list(frequency_values.keys())

selected_file_path = ""
# Function to read the CSV file and plot the data
def display_file_content(file_path):
    try:
        data = pd.read_csv(file_path)
        plot_data(data) # calls function to plot data
        global imported_data
        imported_data = data # Store the imported data globally for optimization
    except Exception as e:
        print("Error reading file:", e)

# Function to import a file
def import_file():
    global selected_file_path
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if file_path:
        selected_file_path = file_path
        display_file_content(file_path)

def run_matlab_script():
    try:
        global selected_file_path
        # Start MATLAB engine
        eng = matlab.engine.start_matlab()

        # Add the directory containing your MATLAB script to the MATLAB path
        eng.addpath(r'/Users/kimberly/Documents/MATLAB/IRES-Summer-2024', nargout=0)

        # Run the MATLAB script with the file path as an argument
        eng.ColeReplaceR1WithC(selected_file_path, nargout=0)
        
        # Keep the figures open by preventing MATLAB from closing immediately
        input("Press Enter to close the MATLAB figures and exit...")
        
    except matlab.engine.MatlabExecutionError as e:
        print(f"MATLAB execution error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        eng.quit()

# Function to plot data
def plot_data(data):
    # Clear existing plots
    for widget in frame_plots.winfo_children():
        widget.destroy()
    # Check if necessary columns exist
    required_columns = {'Frequency(Hz)', 'Impedance(Ohm)', 'Phase(degrees)', 'Absolute Resistance(Ohm)', 'Absolute Reactance(Ohm)'}
    if required_columns.issubset(data.columns):
        # Create frequency vs. magnitude plot
        fig1, ax1 = plt.subplots(figsize=(2,1))
        ax1.plot(data['Frequency(Hz)'], data['Impedance(Ohm)'])
        ax1.set_xlabel('Frequency')
        ax1.set_ylabel('Magnitude')
        ax1.set_title('Frequency vs Magnitude')
        canvas1 = FigureCanvasTkAgg(fig1, master=frame_plots)
        fig1.patch.set_alpha(0.0)  # Make the figure background transparent
        ax1.patch.set_alpha(0.0)   # Make the axes background transparent
        canvas1.get_tk_widget().configure(bg=default_bg_color)  # Match the background color
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        # Create frequency vs. phase plot
        fig2, ax2 = plt.subplots(figsize=(2,1))
        ax2.plot(data['Frequency(Hz)'], abs(data['Phase(degrees)']))
        ax2.set_xlabel('Frequency')
        ax2.set_ylabel('Phase')
        ax2.set_title('Frequency vs Phase')
        canvas2 = FigureCanvasTkAgg(fig2, master=frame_plots)
        fig2.patch.set_alpha(0.0)  # Make the figure background transparent
        ax2.patch.set_alpha(0.0)   # Make the axes background transparent
        canvas2.get_tk_widget().configure(bg=default_bg_color)  # Match the background color
        canvas2.draw()
        canvas2.get_tk_widget().grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        # Create resistance vs. -reactance plot
        fig3, ax3 = plt.subplots(figsize=(2,1))
        ax3.plot(data['Absolute Resistance(Ohm)'], abs(data['Absolute Reactance(Ohm)']))
        ax3.set_xlabel('Resistance')
        ax3.set_ylabel('-Reactance')
        ax3.set_title('Resistance vs -Reactance')
        canvas3 = FigureCanvasTkAgg(fig3, master=frame_plots)
        fig3.patch.set_alpha(0.0)  # Make the figure background transparent
        ax3.patch.set_alpha(0.0)   # Make the axes background transparent
        canvas3.get_tk_widget().configure(bg=default_bg_color)  # Match the background color
        canvas3.draw()
        canvas3.get_tk_widget().grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky='nsew')
    else:
        print("Error: The required columns are not present in the data.")

# Create main window
root = tk.Tk()
root.title("Optimization")
default_bg_color = root.cget('bg')

# Set the window size
root.geometry("1100x600")

# Create a frame for the settings
frame_settings = tk.Frame(root, bg=default_bg_color)
frame_settings.grid(row=0, column=0, rowspan=1, columnspan=1, padx=10, pady=10, sticky='nsew')

# Create a frame for the plots
frame_plots = tk.Frame(root, bg=default_bg_color)
frame_plots.grid(row=2, column=0, rowspan=2, columnspan=3, padx=10, pady=10, sticky='nsew')

# Button for import file
import_button = tk.Button(frame_settings, text="Import File", command=import_file)
import_button.grid(column=0, row=0, padx=10, pady=10, sticky='NW')

# Button for optimization
optimization_button = tk.Button(frame_settings, text="Optimize", command=run_matlab_script) # implement command 
optimization_button.grid(column=0, row=1, padx=10, pady=10, sticky='NW')

# Model label and dropdown
model_label = tk.Label(frame_settings, text="Model:")
model_label.grid(column=3, row=0, padx=5, pady=5, sticky='NW')
n = tk.StringVar
model_dropdown = ttk.Combobox(frame_settings, textvariable=n)
model_dropdown.grid(column=4,row=0, padx=5, pady=5, sticky='NW')
model_dropdown['values'] = ('Cole Model', 'Double Cole Model', 'Wood Tissue Model', 'Single Cole Model with Warburg Element')
 
# Lower Bound Frequency
slider_label1 = tk.Label(frame_settings, text="Lower Bound Frequency:")
slider_label1.grid(column=1, row=0, padx=5, pady=5, sticky='NW')
slider1 = ttk.Entry(frame_settings)
slider1.grid(column=2, row=0, padx=5, pady=5, sticky='NW')

# Upper Bound Frequency
slider_label2 = tk.Label(frame_settings, text="Upper Bound Frequency:")
slider_label2.grid(column=1, row=1, padx=5, pady=5, sticky='NW')
slider2 = ttk.Entry(frame_settings)
slider2.grid(column=2, row=1, padx=5, pady=5, sticky='NW')

# Make the main window's grid layout adjustable
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=3)
root.rowconfigure(3, weight=3)

# Make the frame expand with the window
frame_plots.columnconfigure(0, weight=1)
frame_plots.columnconfigure(1, weight=1)
frame_plots.columnconfigure(2, weight=1)
frame_plots.rowconfigure(0, weight=1)
frame_plots.rowconfigure(1, weight=1)
frame_plots.rowconfigure(2, weight=1)

# Configure grid layout for frame_settings
frame_settings.columnconfigure(0, weight=1)
frame_settings.columnconfigure(1, weight=1)
frame_settings.columnconfigure(2, weight=1)
frame_settings.rowconfigure(0, weight=1)
frame_settings.rowconfigure(1, weight=1)

# Run the application
root.mainloop()
