#################################################################################
##   MSP430G2xx3 based BattLab-One Production Version 1.01
##
##   Doug Peters
##   Bluebird Labs LLC.
##   www.bluebird-labs.com
##   February 2019
##   Built with CCS V7.0
##
##   Copyright (c) 2020, Bluebird Labs LLC
##   All rights reserved.
##
##   Redistribution and use in source and binary forms, with or without
##   modification, are permitted provided that the following conditions
##   are met:
##
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in the
##     documentation and/or other materials provided with the distribution.
##
##   * Neither the name of Bluebird Labs LLC nor the names of
##     its contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
##  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
##  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
##  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
##  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
##  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
##  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
##  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
##  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
##  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
##  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
#################################################################################

import tkinter as tk
from tkinter import ttk
from tkinter import *
import csv
from csv import reader
import time
import datetime
import serial
import serial.tools.list_ports
from serial.tools import list_ports
import matplotlib
from matplotlib.widgets import Cursor
import matplotlib.pyplot as plt
import platform
from tkinter import colorchooser
from tkinter import font
import os
import pkg_resources.py2_warn
from tkinter import messagebox
from tkinter import filedialog
import webbrowser
from matplotlib.widgets import RectangleSelector
from matplotlib.widgets import Button
from matplotlib.backend_bases import key_press_handler

matplotlib.use('TkAgg')

#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

#################################################################################    
###     SETUP ROOT, FRAMES, & MATPLOTLIB CANVAS
#################################################################################

def GetIconPath():
   if platform.system() == 'Linux':
      return '@icons\\bbirdlogo.xbm'
   else:
      return 'icons\\bbirdlogo.ico'

root = tk.Tk()
#root.wm_title('BattLab One Version 1.1.1')
root.resizable(False,False)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

#root.iconbitmap('bbirdlogo.ico')
root.iconbitmap(GetIconPath())

s = ttk.Style() 
s.configure('TLabelframe', background='dark gray')

profile_frame = ttk.Frame(root,style='TLabelframe', width = 800, height = 600)
profile_frame.grid(row=0, column=0, padx=5,pady=(1,1),sticky = 'n')

def openBBL():
   webbrowser.open_new('http://bluebird-labs.com')

#img = PhotoImage(file='bbirdlogo_png1.png')
img = PhotoImage(file=os.path.join('icons','bbirdlogo_png1.png'))

logo_button = tk.Button(profile_frame,image=img,command=openBBL,state=tk.NORMAL)
logo_button.grid(row=25,column=0,rowspan=4, padx=(10,4),pady=(5,5),sticky = 'sw')

frame = ttk.Frame(profile_frame, borderwidth=5, relief='sunken', width=800, height=600)
frame.grid(row=0, column=1, rowspan=25, padx=(3,10),pady=(1,1), sticky='n')

frame1 = ttk.Frame(profile_frame, borderwidth=5, relief='sunken', width=800, height=400)
frame1.grid(row=20, column=1, rowspan=25, padx=(10,10),pady=(5,15), sticky='e')

w = Canvas(frame, width=800, height=400)
w.config(background='black')
w.grid(row=0,column = 3,padx=5,pady=(5,5),sticky = 'n')

w1 = Canvas(frame1, width=250, height=200)
w1.config(background='black')
w1.grid(padx=5,pady=(5,5),sticky = 'se')

#################################################################################
###   SETUP GLOBAL VARIABLES
#################################################################################
global si,x,y,s_x,s_y,avg_active_event_I, line_color, sleep_timer,soc_file, u

x = []
y = []
s_x = []
s_y = []
si = []
soc = []
ocv = []
esr = []
soc_tab = []
ocv_tab = []
esr_tab = []
dc = []
dc1 = []
u = 0

lo_offset=tk.DoubleVar()
lo_offset.set(0)

sleep_timer=tk.IntVar()
sleep_timer.set(1)

LSB=0.0025
#LSB=0.0003125

line_color = StringVar()
line_color.set("blue")

line_width = DoubleVar()
line_width.set(0.5)

reading = StringVar()

CAL_12_data = StringVar()
CAL_15_data = StringVar()
CAL_24_data = StringVar()
CAL_30_data = StringVar()
CAL_36_data = StringVar()
CAL_37_data = StringVar()
CAL_42_data = StringVar()
CAL_45_data = StringVar()

Offset_12_data = StringVar()
Offset_15_data = StringVar()
Offset_24_data = StringVar()
Offset_30_data = StringVar()
Offset_36_data = StringVar()
Offset_37_data = StringVar()
Offset_42_data = StringVar()
Offset_45_data = StringVar()

sense_resistor = tk.DoubleVar()
sense_resistor.set(0.165)

sense_resistor_LO = tk.DoubleVar()
sense_resistor_LO.set(99)

data = tk.StringVar()
version = tk.StringVar()

soc_file = tk.StringVar()
soc_file.set('SOC_profiles/AA_AAA.csv')

samples= tk.IntVar()
samples.set(4)

#################################################################################
###   GET SERIAL PORT AND CONNECT
#################################################################################

baud_rate = 115200
com_port = "NONE"

def get_ports():
   ports = list(serial.tools.list_ports.comports())
   cpl = []
   for p in ports:
      cpl.append(p.device)   
   return cpl

def popupmsg(msg):
    popup = tk.Tk()
    #popup.iconbitmap('bbirdlogo.ico')
    popup.iconbitmap(GetIconPath())
    popup.wm_title("About")
    label = ttk.Label(popup, text=msg,)
    label.grid(row=0,column=0, padx=(10,10),pady= (10,10),sticky = 'nsew')
    pop_up_button = tk.Button(popup, text="Okay",command = popup.destroy,state=tk.NORMAL)
    pop_up_button.grid(row=3,column=0,padx=30,pady=(10,10),sticky = 'w')
    popup.mainloop()

def popupmsg1(msg):
    popup1 = tk.Tk()
    #popup1.iconbitmap('bbirdlogo.ico')
    popup1.iconbitmap(GetIconPath())
    popup1.wm_title("Sleep Capture Duration")
    label2 = ttk.Label(popup1, text="Current Duration in Seconds = "+ str(sleep_timer.get()))
    label2.grid(row=1,column=0, padx=(10,10),pady= (10,10),sticky = 'nsew')
    sleep_dur__combo_box = ttk.Combobox(popup1, width=5, textvariable=sleep_timer)
    sleep_dur__combo_box['values'] = (1, 3, 5, 10) 
    sleep_dur__combo_box.grid(row=3, column=0,padx=(150,4),sticky = 'w')
    sleep_dur__combo_box.insert(0,sleep_timer.get())
    def set_sleep_time():
      sleep_timer.set(float(sleep_dur__combo_box.get()))
      popup1.destroy()
    label1 = ttk.Label(popup1, text=msg,)
    label1.grid(row=0,column=0, padx=(10,10),pady= (10,10),sticky = 'nsew')
    pop_up_button2 = tk.Button(popup1, text="Set Time",command = set_sleep_time,state=tk.NORMAL)
    pop_up_button2.grid(row=3,column=0,padx=80,pady=(10,10),sticky = 'w')
    popup1.mainloop()

def popupmsg2(msg):
    popup2 = tk.Tk()
   
   #popup2.iconbitmap('bbirdlogo.ico')
    popup2.iconbitmap(GetIconPath())
      
    popup2.wm_title("Sleep Current Error")
    label2 = ttk.Label(popup2, text=msg,)
    label2.grid(row=0,column=0, padx=(10,10),pady= (10,10),sticky = 'nsew')
    pop_up_button2 = tk.Button(popup2, text="Okay",command = popup2.destroy,state=tk.NORMAL)
    pop_up_button2.grid(row=3,column=0,padx=30,pady=(10,10),sticky = 'w')
    popup2.mainloop()
   
def samplesmsg():
   smp = tk.Tk()
   def set_samples():
      samples.set(int(smp_combo_box.get()))
      if smp_combo_box.get() == '1':
         cmd = 's'
         bytes_returned = ser.write(cmd.encode())  
      if smp_combo_box.get() == '4':
         cmd = 't'
         bytes_returned = ser.write(cmd.encode())
      elif smp_combo_box.get() == '16':
         cmd = 'u'
         bytes_returned = ser.write(cmd.encode())
      elif smp_combo_box.get() == '64':
         cmd = 'v'
         bytes_returned = ser.write(cmd.encode())
      smp.destroy()
   #smp.iconbitmap('bbirdlogo.ico')
   smp.iconbitmap(GetIconPath())
   
   smp.wm_title("Set Sample Number")
   label2 = ttk.Label(smp, text="Select the number of samples for averaging \n\r Number of samples: ",)
   label2.grid(row=0,column=0, padx=(10,10),pady= (10,10),sticky = 'nsew')
   ser.reset_input_buffer()
   cmd = 'p'
   bytes_returned = ser.write(cmd.encode())
   version.set(ser.readline(2).hex())
   
   smp_combo_box = ttk.Combobox(smp, width=3, textvariable=samples)
   if int(version.get(),16) > 1001:
      smp_combo_box['values'] = (1,4,16,64)
   else:
      smp_combo_box['values'] = (4,16,64)
      
   smp_combo_box.grid(row=1, column=0,padx=(110,4),pady=(1,1),sticky = 'w')
   smp_combo_box.insert(0,samples.get())
   smp_button = tk.Button(smp, text="Set Samples",command = set_samples,state=tk.NORMAL)
   smp_button.grid(row=3,column=0,padx=80,pady=(10,10),sticky = 'w')
   
   smp.mainloop()

#ser_port_cct = Label(profile_frame, text="BB1 Port = ",background='dark gray')
#ser_port_cct.grid(row=1, column=0, padx=(10,4),pady=0,sticky = 'w')     

def OpenConnectWindow():
   global ser_port_combo_box
   connect_popup = tk.Tk()
   connect_popup.iconbitmap(GetIconPath()) 
   connect_popup.wm_title("BattLab-One Connection")
   
   label2 = ttk.Label(connect_popup, text="Connect")
   label2.grid(row=0,column=0, padx=(10,10),pady= (10,10),sticky = 'nsew')
   pop_up_button2 = tk.Button(connect_popup, text="Okay",command = connect_popup.destroy,state=tk.NORMAL)
   pop_up_button2.grid(row=3,column=0,padx=30,pady=(10,10),sticky = 'w')
   
   ser_port_combo_box = ttk.Combobox(connect_popup, values = get_ports(), width=10)
   ser_port_combo_box.grid(row=2, column=0,padx=(10,4),sticky = 'w')

   reset_comm = tk.Button(connect_popup,text='Connect',command=lambda:init(str(ser_port_combo_box.get())),state=tk.NORMAL)
   reset_comm.grid(row=2,column=0, padx=(160,4),pady= 0,sticky = 'w')

   reset_list = tk.Button(connect_popup,text='Refresh',command=lambda:update_ports(),state=tk.NORMAL)
   reset_list.grid(row=2,column=0, padx=(100,4),pady= 0,sticky = 'w')
   popup2.mainloop()
   

#################################################################################    
###     GET DEVICE SPECIFIC CALIBRATION DATA
#################################################################################

DEV_SPEC_ADJ_12 = 0.0
DEV_SPEC_ADJ_15 = 0.0006
DEV_SPEC_ADJ_24 = 0.001
DEV_SPEC_ADJ_30 = 0.0
DEV_SPEC_ADJ_36 = 0.0073
DEV_SPEC_ADJ_37 = 0.001
DEV_SPEC_ADJ_42 = 0.0016
DEV_SPEC_ADJ_45 = 0.002
   
def init(ser_port):
   global ser, sense_low,com_port, \
          CAL_ADJ_12, CAL_ADJ_15, CAL_ADJ_24, CAL_ADJ_30, CAL_ADJ_36, CAL_ADJ_37, CAL_ADJ_42, CAL_ADJ_45, \
          Offset_12, Offset_15, Offset_24, Offset_30, Offset_36, Offset_37, Offset_42, Offset_45
     
   try:
      ser = serial.Serial(ser_port, baud_rate, timeout= None)
      #ser_port_cct.configure(text = "Battlab Connected(" + ser.name+")", foreground='green', font=('Arial Bold',10))
      root.wm_title('BattLab-One Version 1.2.0    Battlab Connected(' + ser.name + ')')
      #ser_port_combo_box.delete(0,END)
      #ser_port_combo_box.insert(0,ser.name)

      #Get Calibration data
      cmd = 'j'
      bytes_returned = ser.write(cmd.encode())
      
      CAL_12_data.set(ser.readline(2).hex())
      CAL_12 = int(CAL_12_data.get(),16)/1000
       
      CAL_15_data.set(ser.readline(2).hex())
      CAL_15 = int(CAL_15_data.get(),16)/1000

      CAL_24_data.set(ser.readline(2).hex())
      CAL_24 = int(CAL_24_data.get(),16)/1000

      CAL_30_data.set(ser.readline(2).hex())
      CAL_30 = int(CAL_30_data.get(),16)/1000

      CAL_36_data.set(ser.readline(2).hex())
      CAL_36 = int(CAL_36_data.get(),16)/1000

      CAL_37_data.set(ser.readline(2).hex())
      CAL_37 = int(CAL_37_data.get(),16)/1000

      CAL_42_data.set(ser.readline(2).hex())
      CAL_42 = int(CAL_42_data.get(),16)/1000

      CAL_45_data.set(ser.readline(2).hex())
      CAL_45 = int(CAL_45_data.get(),16)/1000

      #Get Low Current Offset calibration
      Offset_12_data.set(ser.readline(2).hex())
      Offset_12 = int(Offset_12_data.get(),16)/100000 + DEV_SPEC_ADJ_12

      Offset_15_data.set(ser.readline(2).hex())
      Offset_15 = int(Offset_15_data.get(),16)/100000 + DEV_SPEC_ADJ_15

      Offset_24_data.set(ser.readline(2).hex())
      Offset_24 = int(Offset_24_data.get(),16)/100000 + DEV_SPEC_ADJ_24

      Offset_30_data.set(ser.readline(2).hex())
      Offset_30 = int(Offset_30_data.get(),16)/100000 + DEV_SPEC_ADJ_30

      Offset_36_data.set(ser.readline(2).hex())
      Offset_36 = int(Offset_36_data.get(),16)/100000 + DEV_SPEC_ADJ_36

      Offset_37_data.set(ser.readline(2).hex())
      Offset_37 = int(Offset_37_data.get(),16)/100000 + DEV_SPEC_ADJ_37

      Offset_42_data.set(ser.readline(2).hex())
      Offset_42 = int(Offset_42_data.get(),16)/100000 + DEV_SPEC_ADJ_42

      Offset_45_data.set(ser.readline(2).hex())
      Offset_45 = (int(Offset_45_data.get(),16)/100000) + DEV_SPEC_ADJ_45

      CAL_ADJ_12 = CAL_12
      CAL_ADJ_15 = CAL_15
      CAL_ADJ_24 = CAL_24
      CAL_ADJ_30 = CAL_30
      CAL_ADJ_36 = CAL_36
      CAL_ADJ_37 = CAL_37
      CAL_ADJ_42 = CAL_42
      CAL_ADJ_45 = CAL_45
      
   except serial.SerialException as e:
      messagebox.showinfo("Error No Battlab Device Connected",e)
      pass
      
ports = list(serial.tools.list_ports.comports())

for p in ports:
   
   if p.vid == 0x0403 and p.pid == 0x6001:
      ser_num_prefix = p.serial_number[:2]
      if ser_num_prefix == 'BB':
         com_port = p.device
         init(com_port)

if com_port == 'NONE':
   root.wm_title('BattLab One Version 1.1.1    Not Connected!')
   #ser_port_cct.configure(text="Not Connected!", foreground='red')

def update_ports():
   ports = list(serial.tools.list_ports.comports())
   cpl = []
   for p in ports:
      cpl.append(p.device)
   ser_port_combo_box.configure(values=cpl)

sense_resistor_LO.set(99)


#################################################################################
###    SETUP MENU FUNCTIONS
#################################################################################

    
def OpenFile():
    name = filedialog.askopenfilename(initialdir = 'C:/Users/dwpete3/Desktop',title = 'Select file', \
                                      filetypes = (('CSV Files','*.csv'),('all files','*.*')))

    with open(name, newline='') as csvfile:
       load_profile = csv.reader(csvfile, delimiter=',')
       header = next(load_profile, None)
       if header[0] != 'Battery type':
          popupmsg("File error! \n\r Does not appear to be a Battlab-One file.")
       else:
          for row in load_profile:
             batt_chem.set(row[0])
             battery_capactity_entry_1.delete(0,END)
             battery_capactity_entry_1.insert(0,row[1])
             batt_cells.set(row[2])
             dut_cutoff_voltage_entry.delete(0,END)
             dut_cutoff_voltage_entry.insert(0,row[3])
             voltage.set(row[4])
             rt_dur.delete(0,END)
             rt_dur.insert(0,row[5])
             sl_duration_entry_3.delete(0,END)
             sl_duration_entry_3.insert(0,row[6])
             ae_captured_current_label_4.configure(text=row[7])
             ae_captured_duration_label_4.configure(text=row[8])
             sl_captured_current_label_4.configure(text=row[9])
             sl_captured_duration_label_4.configure(text=row[10])
             dut_cutoff_captured_label_4.configure(text=row[11])
             batt_cap_captured_label_4.configure(text=row[12]),\
             average_current_profile_captured_label_4.configure(text=row[13])
             ae_optimized_current_entry_4.delete(0,END)
             ae_optimized_current_entry_4.insert(0,row[14])
             ae_optimized_duration_entry_4.delete(0,END)
             ae_optimized_duration_entry_4.insert(0,row[15])
             sl_optimized_current_entry_4.delete(0,END)
             sl_optimized_current_entry_4.insert(0,row[16])
             sl_optimized_duration_entry_4.delete(0,END)                                  
             sl_optimized_duration_entry_4.insert(0,row[17])
             dut_cutoff_optimized_entry_4.delete(0,END)                                   
             dut_cutoff_optimized_entry_4.insert(0,row[18])
             batt_cap_optimized_entry_4.delete(0,END)
             batt_cap_optimized_entry_4.insert(0,row[19])
             average_current_profile_optimized_label_4.configure(text=row[20])
             captured_battery_life_hours_graph.configure(text=row[21])
             captured_battery_life_days_graph.configure(text=row[22])
             optimized_battery_life_hours_graph.configure(text=row[23])
             optimized_battery_life_days_graph.configure(text=row[24])

       frame.update()

def SaveFile():
    root.filename =  filedialog.asksaveasfilename(initialdir = 'C:/Users/dwpete3/Desktop',title = 'Select file',
                                filetypes = (('CSV Files','*.csv'),('all files','*.*')))
   
    with open((root.filename+'.csv'), 'w', newline='') as analysis:
       writer = csv.writer(analysis, delimiter=',')         

       writer.writerow(["Battery type",\
                        "Battery Capacity (mAh)",\
                        "Number of Cells",\
                        "DUT Cutoff Voltage (V)",\
                        "PSU Voltage (V)",\
                        "Entered Active Event Duration (S)",\
                        "DUT Sleep Duration (S)",\
                        "Captured Active Event Current (mA)",\
                        "Captured Active Event Duration(S)",\
                        "Captured Sleep Current (uA)",\
                        "Captured DUT Sleep Duration (S)",\
                        "Captured DUT Cutoff Voltage (V)",\
                        "Captured DUT Effective Battery Capacity (mAh)",\
                        "Captured Total Current Profile (mA)",\
                        "Optimized Active Event Current (S)",\
                        "Optimized Active Event Duration (mA)",\
                        "Optimized Sleep Event Current (uA)",\
                        "Optimized Sleep Event Duration (S)",\
                        "Optimized DUT Cutoff Voltage (V)",\
                        "Optimized Effective Battery Capacity (mAh)",\
                        "Optimized Total Current Profile (mA)",\
                        "Captured Battery Life (Hours)",\
                        "Captured Battery Life (Days)",\
                        "Optimized Battery Life (Hours)",\
                        "Optimized Battery Life (Days)"])
       
       writer.writerow([batt_chem.get(), \
                        battery_capactity_entry_1.get(),\
                        batt_cells.get(),\
                        dut_cutoff_voltage_entry.get(),\
                        psu_combo_box.get(),\
                        runtime_duration.get(),\
                        sleep_duration.get(),\
                        ae_captured_current_label_4.cget("text"),\
                        ae_captured_duration_label_4.cget("text"),\
                        sl_captured_current_label_4.cget("text"),\
                        sl_captured_duration_label_4.cget("text"),\
                        dut_cutoff_captured_label_4.cget("text"),\
                        batt_cap_captured_label_4.cget("text"),\
                        average_current_profile_captured_label_4.cget("text"),\
                        ae_optimized_current_entry_4.get(),\
                        ae_optimized_duration_entry_4.get(),\
                        sl_optimized_current_entry_4.get(),\
                        sl_optimized_duration_entry_4.get(),\
                        dut_cutoff_optimized_entry_4.get(),\
                        batt_cap_optimized_entry_4.get(),\
                        average_current_profile_optimized_label_4.cget("text"),\
                        captured_battery_life_hours_graph.cget("text"),\
                        captured_battery_life_days_graph.cget("text"),\
                        optimized_battery_life_hours_graph.cget("text"),\
                        optimized_battery_life_days_graph.cget("text")])  
               
    analysis.close
    
def export_ae_data(): #Save active event data to Outputfile
           
   rows = zip(x,y)

   root.filename =  filedialog.asksaveasfilename(initialdir = 'C:/Users/dwpete3/Desktop',title = 'Select file',
                                filetypes = (('CSV Files','*.csv'),('all files','*.*')))
   
   with open((root.filename + '.csv'), 'w', newline='') as analysis:
      writer = csv.writer(analysis, delimiter=',')
      for row in rows:
         writer.writerow(row)
   analysis.close()

def export_s_data(): #Save sleep event data to Outputfile
           
   rows = zip(s_x,s_y)

   root.filename =  filedialog.asksaveasfilename(initialdir = 'C:/Users/dwpete3/Desktop',title = 'Select file',
                                filetypes = (('CSV Files','*.csv'),('all files','*.*')))
   
   with open((root.filename + '.csv'), 'w', newline='') as analysis:
      writer = csv.writer(analysis, delimiter=',')
      for row in rows:
         writer.writerow(row)
   analysis.close()
   
   
def Linecolor():
    ln_color, hex_color = colorchooser.askcolor(parent=frame,initialcolor=(255, 0, 0)) 
    if hex_color == None:
       line_color.set("blue")
    else:
       line_color.set(hex_color)

def SleepDurationTime():
    popupmsg1("Please choose the duration for sleep capture mode in seconds")

def set_sample_number():
   samplesmsg()

def set_sense_resistor_behavior():
   sensemsg()
   
#def get_config():
 #  ser.reset_input_buffer()
 #  cmd = 'm'
 #  bytes_returned = ser.write(cmd.encode())
 #  data.set(ser.readline(2).hex())
 #  print('MFR CAL ',data.get())
 #  data.set(ser.readline(2).hex())
#   print('ADC CONFIG ',data.get())
   
def About():
    #messagebox.showinfo("Battlab-One Version 1.0 \n\r Contact www.bluebird-labs.com/support for issues")
   ser.reset_input_buffer()
   cmd = 'p'
   bytes_returned = ser.write(cmd.encode())
   version.set(ser.readline(2).hex())
   popupmsg("Battlab-One Version 1.0 \n\r Contact www.bluebird-labs.com/support for issues" + "\n\r Firmware Version " + str(int(version.get(),16)/1000))

def Disclaimer():
   popupmsg(' \n \
             Bluebird Labs LLC. \n\
             Copyright (c) 2020, Bluebird Labs LLC \n\
             All rights reserved.\n\
             \n\
             THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" \n\
             AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, \n\
             THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR \n\
             PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR \n\
             CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, \n\
             EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, \n\
             PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; \n\
             OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, \n\
             WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR \n\
             OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, \n\
             EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.')


def quitapp(window):
   if messagebox.askokcancel("Quit", "Do you want to quit?"):
      try:
         cmd = 'i' #Turn off the PSU
         bytes_returned = ser.write(cmd.encode())
         ser.close()
      except:
         pass
      window.quit()
      root.destroy()


#################################################################################
###   SETUP MENU SYSTEM
#################################################################################
menu = Menu(root)

root.config(menu=menu)

filemenu = Menu(menu)
menu.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='Open', command=OpenFile)
filemenu.add_command(label='Save', command=SaveFile, state=DISABLED)
filemenu.add_command(label='Export Active Event Data', command=export_ae_data, state=DISABLED)
filemenu.add_command(label='Export Sleep Event Data', command=export_s_data, state=DISABLED)
filemenu.add_separator()
filemenu.add_command(label='Exit', command=lambda arg=root:quitapp(arg))

optionsmenu = Menu(menu)
menu.add_cascade(label='Connect', menu=optionsmenu)
optionsmenu.add_command(label='Select COM', command=OpenConnectWindow)

optionsmenu = Menu(menu)
menu.add_cascade(label='Options', menu=optionsmenu)
optionsmenu.add_command(label='Line Color', command=Linecolor)
optionsmenu.add_command(label='Sleep Current Capture Duration', command=SleepDurationTime)
optionsmenu.add_command(label='Sample Number', command=set_sample_number)

#optionsmenu.add_command(label='Get CONFIG...', command=get_config)

helpmenu = Menu(menu)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='About', command=About)
helpmenu.add_command(label='Disclaimer', command=Disclaimer)

#################################################################################
####    MATPLOTLIB FOR ACTIVE AND SLEEP CURRENT PLOTS
#################################################################################

class CustomToolbar(NavigationToolbar2Tk):
   def s_range():
      pass

   def __init__(self,canvas_,parent_):
        self.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            (None, None, None, None),
            ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            ('Save', 'Save the plot', 'filesave', 'save_figure'),
            (None, None, None, None),
            ('Select range', 'Select data range', 'home', 's_range'),
            )
        NavigationToolbar2Tk.__init__(self,canvas_,parent_)

def data_plot(x,y,voltage, minimum, maximum, duration, current,type):
    #PLOT THE DATA

    global ax, f, axs, fs, toggle_selectorRS, toggle_selectorRS1, toolbar, line_select_callback, canvas
    
    def format_coord(x, y):
       return 'mS ={:3.1f}, mA ={:3.3f}'.format(x, y)
    
    def line_select_callback(eclick, erelease):
       #'eclick and erelease are the press and release events'
        sum_y = 0.0
        count_y =0
        avg_y=0

        select_duration_range_entry_1.delete(0,END)
        select_current_range_entry_1.delete(0,END)
        
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        if x1 < 0 or x2 < 0 :
           select_duration_range_entry_1.insert(0,'OL')
           select_current_range_entry_1.insert(0,'OL')

        else:  
           x_start = int(round(eclick.xdata,0))
           x_stop = int(round(erelease.xdata,0))
           
           select_duration_range_entry_1.insert(0,round((erelease.xdata-eclick.xdata),2))

           for ac in range(x_start,x_stop,1):
              sum_y= sum_y + y[ac]
              count_y = count_y + 1
        try:
           avg_y = sum_y/count_y
           select_current_range_entry_1.insert(0,round(avg_y,4))
        except:
           select_duration_range_entry_1.insert(0,'OL')
           select_current_range_entry_1.insert(0,'OL')
           
   # Select Active Event Range
    def select_range():

       if toolbar.mode == 'zoom rect':
          toolbar.zoom(False)
       toggle_selectorRS.set_active(True) 
      # toggle_selectorRS1.set_active(True)  

    if type == 'Active':

       f = plt.figure(figsize=(8, 4.5), dpi=100,clear=True)
       
       if plot_active_var.get() == 1:
          ax = f.add_subplot(111)
          toolbar.update()
       else:
          ax = f.add_subplot(212)
          axs = f.add_subplot(211)

       plt.style.use('fast')
       plt.autoscale()
       
       ax.set_title('Active Event Profile', fontsize=9)
       axs.set_title('Sleep Current Profile', fontsize=9)

       #ax.set_title('Active Event Profile: ' + 'Voltage: ' + voltage + ' volts   '  +'Capture Time:  '+ duration + ' seconds' + \
       #                '\n' + 'Minimum: '  + minimum + 'mA    ' + 'Maximum: '+ maximum + 'mA    ' + 'Average Active Current: ' + current + 'mA    ', \
       #                   fontsize=9)
       #axs.set_title('Sleep Current Profile: ' + 'Voltage' + voltage + ' volts   '  +'Capture Time:  '+  duration + ' seconds' + \
       #                '\n' + 'Minimum: '  + minimum + 'mA    ' + 'Maximum: '+ maximum + 'mA    ' + 'Average Sleep Current: ' + \
       #                   current + 'mA    ', fontsize=9)

       ax.set_xlabel('Time in Milliseconds')
       ax.set_ylabel('Current in Milliamps')
       axs.set_ylabel('Current in Milliamps')
       
      
       ax.plot(x, y, color=line_color.get(), linewidth=line_width.get())
       
       ax.grid(b=True, which='major', axis='both',color='black', linestyle='-', linewidth=.1)
       axs.grid(b=True, which='major', axis='both',color='black', linestyle='-', linewidth=.1)

       canvas = FigureCanvasTkAgg(f, master=w)
       canvas.get_tk_widget().grid(row=0,column=6)
       
       toolbarFrame = ttk.Frame(master=frame)
       toolbarFrame.grid(row=14, column=3, sticky='w' )
       toolbar = CustomToolbar(canvas, toolbarFrame)

       ax.format_coord = format_coord
       axs.format_coord = format_coord

       #toolbar.children['!button8'].config(command=select_range)
       
       toggle_selectorRS = RectangleSelector(ax, line_select_callback,\
                                       drawtype='box', useblit=True,\
                                       button=[1, 3],  \
                                       minspanx=5, minspany=5,\
                                       spancoords='pixels',\
                                       interactive=True,\
                                       rectprops = dict(facecolor='tomato', edgecolor = 'black', alpha=0.2, fill=True))
       
       toggle_selectorRS.set_active(False)  

      # toggle_selectorRS1 = RectangleSelector(axs, line_select_callback,\
      #                                 drawtype='box', useblit=True,\
      #                                 button=[1, 3],  \
      #                                 minspanx=5, minspany=5,\
      #                                 spancoords='pixels',\
      #                                 interactive=True,\
      #                                 rectprops= dict(facecolor='blue', edgecolor = 'black', alpha=0.2, fill=True))
       
      # toggle_selectorRS1.set_active(False)

       f.tight_layout(pad=1.00)

       toolbar.update()
       
       canvas.draw()
       

    else:
       axs.grid(b=True, which='major', axis='both',color='black', linestyle='-', linewidth=.1)
       
       if avg_sleep_event_I.cget("text") == "OL":
          axs.set_title('Overflow - Sleep Current less than 10 uA', color = 'red', fontsize=12)

       else: 
          axs.set_title('Sleep Current Profile', fontsize=9)
       
       plt.autoscale()
       axs.set_ylabel('Current in Milliamps')
       axs.plot(x, y, color=line_color.get(), linewidth=line_width.get()) 
      # axs.grid(b=True, which='major', axis='both',color='black', linestyle='-', linewidth=.1)
       canvas.draw()
   

#################################################################################
###    SETUP STATE OF CHARGE GRAPH
#################################################################################   
def update_soc_chart(eventObject):
    global ax1, f1, new_bat_cap

    try:
       float(dut_cutoff.get())
    except ValueError:
       popupmsg("Please only enter 0123456789.")
    
    f1 = plt.figure(figsize=(3.5, 1.8), dpi=100,clear=False)
    ax1 = f1.add_subplot(111)

   # Clear the plot
    soc_tab[:] = []
    ocv_tab[:] = []
    esr_tab[:] = []
    dc[:] = []
    dc1[:] = []
    soc_state = 0
    curve = 0
    batt_cap_optimized_entry_4.delete(0,END)
    
    ax1.plot(soc_tab, ocv_tab)
    ax1.cla()
    
    with open(soc_file.get(), 'r')as csvfile:
       inp1 = csv.reader(csvfile, delimiter = ',')
       headers = next(inp1, None)
       headers1= next(inp1, None)
       headers2 = next(inp1, None)   

       for row in inp1:
          soc_tab.append(int(row[0]))
          ocv_tab.append(float(row[1]))
          esr_tab.append(float(row[2]))

       for i in range(len(ocv_tab)-1):
          if float(ocv_tab[i]) < float(dut_cutoff.get()):
             soc_state=soc_state+1
          curve = ocv_tab[soc_state]
    new_bat_cap = float(1-(soc_state/100))*float(battery_capactity_entry_1.get())
    batt_cap_optimized_entry_4.insert(0,int(new_bat_cap))
    batt_cap_captured_label_4.config(text=str(int(new_bat_cap)))
          
    csvfile.close()
    
    #PLOT THE DATA
    plt.style.use('fast')
    
    ax1.set_title(soc_file.get())
    
 
    ax1.grid(b=True, which='major', axis='both',color='black', linewidth=.1)

    ax1.plot(soc_tab,ocv_tab, color='blue', linewidth=.5)
 
    ax1.plot(soc_state,float(curve), marker='o',color='red', linewidth=1)
    
    ax1.set_xlabel('SOC(%)')
    ax1.set_ylabel('OCV(V)')
    plt.ylim([min(ocv_tab)-.2,max(ocv_tab)+.2])
    ax1.minorticks_on()
    f1.tight_layout()
    ax1.invert_xaxis()

    cursor1 = Cursor(ax1,color=line_color.get(), linewidth=.3)
    
    canvas1 = FigureCanvasTkAgg(f1, master=w1)
    canvas1.get_tk_widget().grid(row=1,column=1,sticky='w')

    #toolbar = NavigationToolbar2TkAgg(canvas, toolbarFrame)
    canvas1.draw()
    
#################################################################################
###    SETUP VOLTAGE PARAMETERS
#################################################################################
    
def set_profile_params(eventObject):

    try:
        float(batt_cap.get())
    except ValueError:
        popupmsg("Please only enter 0123456789.")
       
    if ((batt_chem.get() == 'AA-Alkaline' or batt_chem.get() == 'AAA-Alkaline') and batt_cells.get() == '1'):
        psu_combo_box.current(1)
        soc_file.set('SOC_profiles/AA_AAA.csv') 
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,1500)   
        voltage.set(1.5)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,1.0)
    elif((batt_chem.get() == 'AA-Alkaline' or batt_chem.get() == 'AAA-Alkaline') and batt_cells.get() == '2'):
        psu_combo_box.current(3)
        soc_file.set('SOC_profiles/AA_AAA_2.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,1500)
        voltage.set(3.0)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,2.0)
    elif((batt_chem.get() == 'AA-Alkaline' or batt_chem.get() == 'AAA-Alkaline') and batt_cells.get() == '3'):
        psu_combo_box.current(6)
        soc_file.set('SOC_profiles/AA_AAA_3.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,1500)
        voltage.set(4.5)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,3.0)
    elif(batt_chem.get() == 'LI-Ion' and batt_cells.get() == '1'):
        psu_combo_box.current(5)
        soc_file.set('SOC_profiles/LiIon.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,2600)
        voltage.set(4.2)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,3.2)
    elif(batt_chem.get() == 'LiFePO4' and batt_cells.get() == '1'):
        psu_combo_box.current(5)
        soc_file.set('SOC_profiles/LiFePO4.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,1600)
        voltage.set(3.6)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,3.0)
    elif(batt_chem.get() == 'AA-NiMH/NiCd' and batt_cells.get() == '1'):
        psu_combo_box.current(0)
        soc_file.set('SOC_profiles/NiMH_AA.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,1500)
        voltage.set(1.2)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,1.0)
    elif(batt_chem.get() == 'AA-NiMH/NiCd' and batt_cells.get() == '2'):
        psu_combo_box.current(1)
        soc_file.set('SOC_profiles/NiMH_AA_2.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,1500)
        voltage.set(2.4)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,2.0)
    elif(batt_chem.get() == 'AA-NiMH/NiCd' and batt_cells.get() == '3'):
        psu_combo_box.current(4)
        soc_file.set('SOC_profiles/NiMH_AA_3.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,1500)
        voltage.set(3.6)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,3.0)
    elif(batt_chem.get() == 'AAA-NiMH/NiCd' and batt_cells.get() == '1'):
        psu_combo_box.current(0)
        soc_file.set('SOC_profiles/NiMH_AAA.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,1500)
        voltage.set(1.2)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,1.0)
    elif(batt_chem.get() == 'AAA-NiMH/NiCd' and batt_cells.get() == '2'):
        psu_combo_box.current(1)
        soc_file.set('SOC_profiles/NiMH_AAA_2.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,1500)
        voltage.set(2.4)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,2.0)
    elif(batt_chem.get() == 'AAA-NiMH/NiCd' and batt_cells.get() == '3'):
        psu_combo_box.current(4)
        soc_file.set('SOC_profiles/NiMH_AAA_3.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,1500)
        voltage.set(3.6)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,3.0)
    elif(batt_chem.get() == batt_chem.get() == 'CR123' and batt_cells.get() == '1'):
        psu_combo_box.current(4)
        soc_file.set('SOC_profiles/CR123.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,225)
        voltage.set(3.0)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,2.5)
    elif(batt_chem.get() == 'CR2032' and batt_cells.get() == '1'):
        psu_combo_box.current(4)
        soc_file.set('SOC_profiles/CR2032.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,225)
        voltage.set(3.0)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,2.5)
    elif(batt_chem.get() == 'CR1632' and batt_cells.get() == '1'):
        psu_combo_box.current(4)
        soc_file.set('SOC_profiles/CR1632.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,650)
        voltage.set(3.0)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,2.5)
    elif(batt_chem.get() == 'CR2450' and batt_cells.get() == '1'):
        psu_combo_box.current(4)
        soc_file.set('SOC_profiles/CR2450.csv')
        battery_capactity_entry_1.delete(0,END)
        battery_capactity_entry_1.insert(0,650)
        voltage.set(3.0)
        dut_cutoff_voltage_entry.delete(0,END)
        dut_cutoff_voltage_entry.insert(0,2.1)
    else:
        popupmsg('Battery Info Error. \n\r Check number of cells \n\r  Battlab-One has a maximum 4.5V output')

    update_soc_chart(0)

#################################################################################
####     STEP1 SET BATTERY PARAMETERS AND PSU OUTPUT
#################################################################################

def set_battery_voltage():
   #Turn OFF low current sense resistor
   cmd = 'l'
   bytes_returned = ser.write(cmd.encode())
   time.sleep(0.5)
  # print("Pradio",int(p_radio.get()))
  
   if int(p_radio.get()) == 1:
      
      if voltage.get()== '1.2':
         cmd = 'a'
         bytes_returned = ser.write(cmd.encode())
         sense_resistor.set(CAL_ADJ_12)
         lo_offset.set(Offset_12)
      elif voltage.get()== '1.5':
         cmd = 'b'
         bytes_returned = ser.write(cmd.encode())
         sense_resistor.set(CAL_ADJ_15)
         lo_offset.set(Offset_15)
      elif voltage.get()== '2.4':
         cmd = 'c'
         bytes_returned = ser.write(cmd.encode())
         sense_resistor.set(CAL_ADJ_24)
         lo_offset.set(Offset_24)
      elif voltage.get()== '3.0':
         cmd = 'd'
         bytes_returned = ser.write(cmd.encode())
         sense_resistor.set(CAL_ADJ_30)
         lo_offset.set(Offset_30)
      elif voltage.get()== '3.2':
         cmd = 'o'
         bytes_returned = ser.write(cmd.encode())
         sense_resistor.set(CAL_ADJ_30)
         lo_offset.set(Offset_30)
      elif voltage.get()== '3.6':
         cmd = 'n'
         bytes_returned = ser.write(cmd.encode())
         sense_resistor.set(CAL_ADJ_36)
         lo_offset.set(Offset_36)
      elif voltage.get()== '3.7':
         cmd = 'e'
         bytes_returned = ser.write(cmd.encode())
         sense_resistor.set(CAL_ADJ_37)
         lo_offset.set(Offset_37)
      elif voltage.get()== '4.2':
         cmd = 'f'
         bytes_returned = ser.write(cmd.encode())
         sense_resistor.set(CAL_ADJ_42)
         lo_offset.set(Offset_42)
      elif voltage.get()== '4.5':
         cmd = 'g'
         bytes_returned = ser.write(cmd.encode())
         sense_resistor.set(CAL_ADJ_45)
         lo_offset.set(Offset_45)

   elif int(p_radio.get()) == 0:
      p_rad.configure(foreground='black',background='dark gray')
      p_rad1.configure(foreground='red',background='dark gray')
      cmd = 'i'
      bytes_returned = ser.write(cmd.encode())

   if trig_PSU_var.get() == 0:
      p_rad.configure(foreground='green',background='dark gray')
      p_rad1.configure(foreground='black',background='dark gray')
      p_radio.set(1)
      cmd = 'h'
      bytes_returned = ser.write(cmd.encode())
   
   update_soc_chart(0)

   capture_active_event_button.configure(state=tk.NORMAL)
   trigger_box.config(state=tk.NORMAL)
   #battery_type_combo_box.configure(state=tk.DISABLED)
   #battery_cells_combo_box.configure(state=tk.DISABLED)
   #psu_combo_box.configure(state=tk.DISABLED)
   rt_dur.configure(state=tk.NORMAL)

   step1_label.configure(foreground='black')
   step2_label.configure(foreground='blue')

#################################################################################
###    STEP2 CAPTURE ACTIVE EVENT
#################################################################################


def TrigArmed():
   if trig_var.get() == 1:
      capture_active_event_button.configure(text="ARM Trigger", foreground='red')
      #Start the data logger
      cmd = 'x'
      bytes_returned = ser.write(cmd.encode())
      time.sleep(0.5)
   else:
    capture_active_event_button.configure(state=tk.NORMAL,text="Capture Active", foreground='black')
    
def capture_profile():
    u = 0
    try:
       float(runtime_duration.get())
      
    except ValueError:
       popupmsg("Please only enter 0123456789.")

    global ae_captured_average_current_2,ae_captured_duration_2, max_current, min_current, offset, prev_value

    x[:] = []
    y[:] = []
    si[:] = []

    ax.plot(x, y)
    ax.cla()
    plt.close('all')
    
    #data_plot(x,y,str(0),str(0),str(0),str(0),str(0),'Active')

    if trig_PSU_var.get() == 1:
       cmd = 'h'
       bytes_returned = ser.write(cmd.encode())
       p_rad.config(foreground='green')
       p_rad1.config(foreground='black')
    
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    ser.send_break(duration=0.25)
    
    ae_captured_average_current_2 = 0
    ae_captured_duration_2 = 0
    counter = 0
    cntr = DoubleVar()
    reading = StringVar()
    t=0

    prev_value='NONE'
    
    my_file=open('raw_byte_file.txt', mode='w+', buffering =(10*1024*1024))


    #USE TRIGGER FOR CAPTURE
    if trig_var.get()==1:
       
        progress_label.config(text = 'Capturing...' )
        progress_label.config(foreground = 'red' )

        #Start the data logger
        cmd = 'x'
        bytes_returned = ser.write(cmd.encode())
        #time.sleep(0.5)
        
        while (True):
            if ser.in_waiting > 0:         
                my_file.write(str(t))
                my_file.write(',')
                reading.set(ser.readline(2).hex())
                my_file.write(str(reading.get()))
                
                my_file.write('\n')
                t=t+1
                root.update()
                if str(reading.get()) == '0000' and prev_value == 'ffff':
                    break

                prev_value = str(reading.get())

        cmd = 'y'
        bytes_returned = ser.write(cmd.encode())

        my_file.close()

        progress_label.config(text = 'Complete' )
        progress_label.config(foreground = 'green' )

        if trig_var.get() == 1:
           capture_active_event_button.configure(text="ARM Trigger", foreground='red')
        else:
           capture_active_event_button.configure(text="Capture Active", foreground='black')

        #USE TIME (DURATION) FOR CAPTURE

    else:
        
        pb_vd = ttk.Progressbar(profile_frame, orient='horizontal', mode='determinate',
                                maximum = float(runtime_duration.get()),length=100, variable=cntr)
        
        pb_vd.grid(row=7,column = 0,columnspan=1,padx=(215,1),sticky = 'w')
        pb_vd.start()
    
        progress_label.config(text = 'Capturing...' )
        progress_label.config(foreground = 'red' )
        
        cmd = 'z'
        bytes_returned = ser.write(cmd.encode())
        
      
        offset=time.time()
        #while counter < (float(runtime_duration.get())*0.81):   
        while counter < (float(runtime_duration.get())): 
            my_file.write(str(t))
            my_file.write(',')
            reading.set(ser.readline(2).hex())
            my_file.write(str(reading.get()))
            my_file.write('\n')
            t=t+1
            root.update()
        
            counter = time.time()-offset
            cntr.set(counter)
            profile_frame.update()

        cmd = 'y'
        bytes_returned = ser.write(cmd.encode())
        
        pb_vd.stop()
        pb_vd.destroy()
      
        progress_label.config(text = 'Complete')
        progress_label.config(foreground = 'green')
       
    my_file.close()
    
    with open('raw_byte_file.txt', 'r')as csvfile:
        t=0
        inp = csv.reader(csvfile, delimiter = ',')
        for row in inp:        
            if round((int(row[1],16)*LSB)/float(sense_resistor.get()),5) < 500 \
                  and round((int(row[1],16)*LSB)/float(sense_resistor.get()),5) > 0.0:
              x.append(t)
              y.append(round((int(row[1],16)*LSB)/float(sense_resistor.get()),5))
              t=t+1
            else:
              u=u+1  #Do Nothing

    csvfile.close()
    
    try:
       x.pop()
       y.pop()
    except:
       reset()
   
    #Gather data and statistics
    try:
       ae_captured_average_current_2 = sum(y)/(len(y))
       ae_captured_duration_2 = (max(x)-min(x))/1000
       max_current = round(max(y),3)
       min_current = round(min(y),3)
       average_current_profile_data.configure(text=str(round(ae_captured_average_current_2,3)))
       max_data.configure(text=str(max_current))
       min_data.configure(text=str(min_current))
       avg_active_event_I_2.configure(text=str(round(ae_captured_average_current_2,2)))

       #Fill out partial Step 4 Actuals  
       ae_captured_current_label_4.configure(text=str(round(float(ae_captured_average_current_2),3)), foreground='black',background='dark gray') 
       ae_captured_duration_label_4.configure(text=str(round(float(ae_captured_duration_2),3)), foreground='black',background='dark gray')
       dut_cutoff_captured_label_4.configure(text=str(float(dut_cutoff_voltage_entry.get())), foreground='black',background='dark gray')

       data_plot(x,y,voltage.get(),str(min_current),str(round(max_current,2)),str(round(ae_captured_duration_2,2)), \
          str(round(ae_captured_average_current_2,2)),'Active')

       #Copy partial Step 4 Actuals to Optimized
       ae_optimized_current_entry_4.delete(0,END)
       ae_optimized_current_entry_4.insert(0,str(round(float(ae_captured_average_current_2),3)))
       ae_optimized_duration_entry_4.delete(0,END)
       ae_optimized_duration_entry_4.insert(0,str(round(float(ae_captured_duration_2),3)))
       dut_cutoff_optimized_entry_4.delete(0,END)
       dut_cutoff_optimized_entry_4.insert(0,str(float(dut_cutoff_voltage_entry.get())))
    except:
       reset()
       
    avg_active_event_I_2.configure(foreground='green',state=tk.NORMAL)
    avg_active_event_I_units.configure(foreground='green',state=tk.NORMAL)

    #capture_active_event_button.config(state=tk.DISABLED)
  
    export_ae_button.configure(state=tk.NORMAL)
    filemenu.entryconfigure(3,state=tk.NORMAL)
    capture_sleep_btn_3.configure(state=tk.NORMAL)
    
    step2_label.configure(foreground='black')
    step3_label.configure(foreground='blue')
    sl_duration_entry_3.configure(state=tk.NORMAL)
        
    os.remove('raw_byte_file.txt')
      
#################################################################################
###    STEP3 CAPTURE SLEEP CURRENT
#################################################################################

def capture_sleep_profile():
   global sl_captured_average_current_3, total_event_duration,\
   average_current_all_events, progress_label_s, new_bat_cap
      
   try:
       float(sleep_duration.get())
      
   except ValueError:
       popupmsg("Please only enter 0123456789.")
       
   s_x[:] = []
   s_y[:] = []
   t=0
   soc_state = 0
   si[:] = []
   sl_select_shunt(0)

   axs.plot(s_x, s_y)
   axs.cla()
   plt.close('all')
    
   #data_plot(s_x,s_y,str(0),str(0),str(0),str(0),str(0),'Sleep')

   avg_sleep_event_I_units.configure(state=tk.NORMAL)

   ser.reset_input_buffer()
   ser.reset_output_buffer()
    
   sleep_reading = StringVar()
   counter1 = 0    
   cntr1 = DoubleVar()

   pb_vd_s = ttk.Progressbar(profile_frame, orient='horizontal', mode='determinate',
                                maximum = sleep_timer.get(),length=100, variable=cntr1)
        
   pb_vd_s.grid(row=10,column = 0,columnspan=1,padx=(215,1),sticky = 'w')
   pb_vd_s.start()
    
   progress_label_s.config(text = 'Capturing...' )
   progress_label_s.config(foreground = 'red' )
   
   if sl_shunt_var.get() == '800uA - 500mA': #Lo current shunt is OFF
      ser.reset_input_buffer()
      ser.reset_output_buffer()
      sleep_file=open('sleep_current.txt', mode='w', buffering =(10*1024*1024))
      offset1=time.time()
      time.sleep(0.5)
      
      cmd = 'z'
      bytes_returned = ser.write(cmd.encode())

      while counter1 < sleep_timer.get()*1.6:
         sleep_file.write(str(t))
         sleep_file.write(',')
         sleep_reading.set(ser.readline(2).hex())
         if round((int(sleep_reading.get(),16)*LSB)/float(sense_resistor.get()),6) < 500 \
                  and round((int(sleep_reading.get(),16)*LSB)/float(sense_resistor.get()),6) != 0.0:
           si.append(round((int(sleep_reading.get(),16)*LSB)/float(sense_resistor.get()),6))
           sleep_file.write(str(round((int(sleep_reading.get(),16)*LSB)/float(sense_resistor.get()),6)))
           sleep_file.write('\n')
         t=t+1
         root.update()
         counter1 = time.time()-offset1
         cntr1.set(counter1)
         profile_frame.update()

      pb_vd_s.stop()
      pb_vd_s.destroy()
      
      cmd = 'y'
      bytes_returned = ser.write(cmd.encode())
      
      time.sleep(1)
      sleep_file.close()
      progress_label_s.config(text = 'Complete')
      progress_label_s.config(foreground = 'green')
      
      sl_captured_average_current_3 = (sum(si)/(len(si)))- lo_offset.get() #Input bias current minus Offset voltage calibration

      if sl_captured_average_current_3 < .811:
         avg_sleep_event_I_units.configure(text='')
         progress_label_s.config(foreground='red',text="Overflow")
         avg_sleep_event_I.configure(foreground='red')
         popupmsg2("Sleep current out of range. Try using the 10uA - 800uA range.\n\rCaptured sleep current < 800uA")
         sl_captured_average_current_3 = 0
      else:
         avg_sleep_event_I.configure(text=str(round(sl_captured_average_current_3,2)))
         avg_sleep_event_I.configure(state=tk.NORMAL)
         avg_sleep_event_I.configure(foreground='green')
         avg_sleep_event_I_units.configure(text='mA')
         avg_sleep_event_I_units.configure(foreground='green')
     
   elif sl_shunt_var.get() == '10uA - 800uA': #Lo current shunt is ON:   
      ser.reset_input_buffer()
      ser.reset_output_buffer()
      sleep_file=open('sleep_current.txt', mode='w', buffering =(10*1024*1024))
   
      time.sleep(0.5)

      offset1=time.time()
      cmd = 'z'
      bytes_returned = ser.write(cmd.encode())

      while counter1 < sleep_timer.get():
         sleep_file.write(str(t))
         sleep_file.write(',')
         sleep_reading.set(ser.readline(2).hex())
         if round((int(sleep_reading.get(),16)*LSB)/float(sense_resistor_LO.get()),6) < 812 \
                  and round((int(sleep_reading.get(),16)*LSB)/float(sense_resistor_LO.get()),6) != 0.0:
            si.append(round((int(sleep_reading.get(),16)*LSB)/float(sense_resistor_LO.get()),6))
            sleep_file.write(str(round((int(sleep_reading.get(),16)*LSB)/float(sense_resistor_LO.get()),6)))
            sleep_file.write('\n')
         t=t+1
         root.update()
         counter1 = time.time()-offset1
         cntr1.set(counter1)
         profile_frame.update()

      pb_vd_s.stop()
      pb_vd_s.destroy()
      
      cmd = 'y'
      bytes_returned = ser.write(cmd.encode())
      sleep_file.close()
      
      if sense_persist_var.get() == 0:
         sl_shunt_var.set('800uA - 500mA')
         sl_shunt_select__combo_box.selection_clear()
         sl_select_shunt(0) 
      
      progress_label_s.config(text = 'Complete')
      progress_label_s.config(foreground = 'green')
     
      sl_captured_average_current_3 = (sum(si)/(len(si)))- lo_offset.get() #Input bias current and Offset voltage calibration

      if round(sl_captured_average_current_3*1000,2) > 811:
         avg_sleep_event_I_units.configure(state=tk.DISABLED)
         progress_label_s.config(foreground='red', text="Overflow")
         avg_sleep_event_I.configure(foreground='red')
         avg_sleep_event_I_units.configure(text='')
         popupmsg2("Sleep current out of range.\n\r Try using the 800uA - 500mA range Captured sleep current > 800uA")
         sl_captured_average_current_3 = 0
      else:
         if round(sl_captured_average_current_3*1000,2) >= 10:
            avg_sleep_event_I.configure(text=str(round(sl_captured_average_current_3*1000,2)))
            avg_sleep_event_I.configure(foreground='green')
            avg_sleep_event_I_units.configure(state=tk.NORMAL)
            avg_sleep_event_I_units.configure(text='uA')
            avg_sleep_event_I_units.configure(foreground='green')
         else:
            progress_label_s.config(foreground='red', text="Overflow")
            avg_sleep_event_I.configure(text="OL")
            avg_sleep_event_I.configure(foreground='red')  

   with open(soc_file.get(), 'r')as csvfile:
      inp = csv.reader(csvfile, delimiter = ',')
      headers = next(inp, None)
      headers1= next(inp, None)
      headers2 = next(inp, None)
      my_list = list(inp)

      for row in inp:
         soc.append(int(row[0]))
         ocv.append(float(row[1]))
         esr.append(float(row[2]))

      for i in range(len(my_list)-1):
         if (float(my_list[i][1])) < float(dut_cutoff_optimized_entry_4.get()):
            soc_state=soc_state+1
         try:
            new_bat_cap = float(1-(soc_state/100))*float(battery_capactity_entry_1.get())
         except:
             u=u+1  #Do Nothing
      
   with open('sleep_current.txt', 'r')as csvfile:
      t=0
      inp = csv.reader(csvfile, delimiter = ',')
      for row in inp:        
         if round(float(row[1]),5)< 500 and round(float(row[1]),5) > 0.0:
            s_x.append(t)
            s_y.append(round(float(row[1])- lo_offset.get(),5))
            t=t+1
         else:
            u=u+1  #Do Nothing


   s_captured_average_current_3 = round((sum(s_y)/(len(s_y))),3)
   s_captured_duration_3 = round(((max(s_x)-min(s_x))/1000),2)
   max_s_current = round(max(s_y),3)
   min_s_current = round(min(s_y),3)

   #Sleep Statistics
   try:
       sl_average_current_profile_data.configure(text=str(round(s_captured_average_current_3,3)))
       sl_max_data.configure(text=str(max_s_current))
       sl_min_data.configure(text=str(min_s_current))
   except:
       reset()

   if plot_active_var.get() == 0:
      data_plot(s_x,s_y,voltage.get(),str(min_s_current),str(max_s_current),str(s_captured_duration_3), str(s_captured_average_current_3),'Sleep')

   csvfile.close()         

   #Update Results Step4 data
      
   total_event_duration = float(sleep_duration.get()) + ae_captured_duration_2

   average_current_all_events = (sl_captured_average_current_3 * float(sleep_duration.get()) \
                                 + (ae_captured_average_current_2*ae_captured_duration_2))/float(total_event_duration)

   #Complete Step 4 Captured Labels
   sl_captured_current_label_4.configure(text=str(round(float(sl_captured_average_current_3),2)), foreground='black',background='dark gray')
   sl_captured_duration_label_4.configure(text=str(round(float(sleep_duration.get()),2)), foreground='black',background='dark gray')
   average_current_profile_captured_label_4.configure(text=str(round(average_current_all_events,2)),foreground='black',background='dark gray')
   batt_cap_captured_label_4.configure(text=str(int(new_bat_cap)), foreground='black',background='dark gray')

   #Copy Step 4 Captured Labels to Optimized Entrys
   sl_optimized_current_entry_4.delete(0,END)
   sl_optimized_current_entry_4.insert(0,str(round(float(sl_captured_average_current_3),2)))
   sl_optimized_duration_entry_4.delete(0,END)
   sl_optimized_duration_entry_4.insert(0,str(round(float(sleep_duration.get()),2)))
   average_current_profile_optimized_label_4.configure(text=str(round(average_current_all_events,2)),foreground='black',background='dark gray')
   batt_cap_optimized_entry_4.delete(0,END)
   batt_cap_optimized_entry_4.insert(0,str(int(new_bat_cap)))

   si.clear()

   calc_battery_life()
   
   use_range_select_button.configure(state=tk.NORMAL)
   sl_use_range_select_button.configure(state=tk.NORMAL)

   #override_dut_cuttoff.configure(state=tk.NORMAL)
   step4_label.configure(foreground='blue')
   
   if os.path.exists('sleep_current.txt'):
      os.remove('sleep_current.txt')

   
#################################################################################
###    STEP4 OPTIMIZED RESULTS 
#################################################################################
def optimize_profile():
   global optimized_battery_life_hours, optimized_battery_life_days, optimized_average_current_all_events
   
   try:
      float(batt_cap_optimized_entry_4.get())
      float(dut_cutoff_optimized_entry_4.get())
      float(sl_optimized_duration_entry_4.get())
      float(sl_optimized_current_entry_4.get())
      float(ae_optimized_duration_entry_4.get())
      float(ae_optimized_current_entry_4.get())
      
   except ValueError:
      popupmsg("Please only enter 0123456789.")
   
   if override_dut_cuttoff_var.get() == 1:
      new_bat_cap = float(batt_cap_optimized_entry_4.get())
   else:
      new_bat_cap = float(batt_cap_optimized_entry_4.get())
      batt_cap_optimized_entry_4.delete(0,END)           
      batt_cap_optimized_entry_4.insert(0,str(int(new_bat_cap)))

   optimized_average_current_all_events = (float(sl_optimized_duration_entry_4.get())* float(sl_optimized_current_entry_4.get()) \
                                           + (float(ae_optimized_duration_entry_4.get())* \
                                              float(ae_optimized_current_entry_4.get())))/(float(sl_optimized_duration_entry_4.get()) \
                                                                                           + float(ae_optimized_duration_entry_4.get()))

   average_current_profile_optimized_label_4.configure(text=str(round(float(optimized_average_current_all_events),4)),\
                                                       foreground='black',background='dark gray')

   #battery_life_hours = capacity in mAH / mA
   optimized_battery_life_hours =  float(new_bat_cap)/float(optimized_average_current_all_events)
   optimized_battery_life_days = float(optimized_battery_life_hours/24)

   optimized_battery_life_hours_graph.configure(text=str(round(float(optimized_battery_life_hours),2)),foreground='blue',background='dark gray')
   optimized_battery_life_days_graph.configure(text=str(round(float(optimized_battery_life_days),2)),foreground='blue',background='dark gray')
   reset_button = tk.Button(profile_frame,text='Reset',command=reset,state=tk.NORMAL)


##################################################################################
####   Calculate Captured Battery Life Hours
##################################################################################
def calc_battery_life():
   #global battery_life_hours, battery_life_days

   try:
      battery_life_hours =  float(new_bat_cap)/float(average_current_all_events)                                 
      battery_life_days = float(battery_life_hours/24)
      captured_battery_life_hours_graph.configure(text=str(round(float(battery_life_hours),2)),foreground='blue',background='dark gray')
      captured_battery_life_days_graph.configure(text=str(round(float(battery_life_days),2)),foreground='blue',background='dark gray')

      optimized_battery_life_hours_graph.configure(text=str(round(float(battery_life_hours),2)),foreground='blue',background='dark gray')
      optimized_battery_life_days_graph.configure(text=str(round(float(battery_life_days),2)),foreground='blue',background='dark gray')  
   except:
      u=u+1                              

   filemenu.entryconfigure(2, state=tk.NORMAL)
   reset_button.configure(state=tk.NORMAL)
   save_button.configure(state=tk.NORMAL)
   #optimize_button.configure(state=tk.NORMAL)
   export_s_button.configure(state=tk.NORMAL)

   step3_label.configure(foreground='black')
   


#################################################################################
###    RESET
#################################################################################

def reset():

    ser.close()
    
    #Reconnect serial port
    ports = list(serial.tools.list_ports.comports())

    for p in ports:
       if p.vid == 0x0403 and p.pid == 0x6001:
          ser_num_prefix = p.serial_number[:2]
          if ser_num_prefix == 'BB':
             com_port = p.device
             init(com_port)

    prev_value = '0000'

    step1_label.configure(foreground='blue')
    step2_label.configure(foreground='black')
    step3_label.configure(foreground='black')
    step4_label.configure(foreground='black')

    #Set sense resistor
    sl_shunt_var.set('800uA - 500mA')
    sl_shunt_select__combo_box.selection_clear()
    sl_select_shunt(0)
         
    #optimize_button.configure(state=tk.DISABLED)
    filemenu.entryconfigure(2, state=tk.DISABLED)
    filemenu.entryconfigure(3, state=tk.DISABLED)
    save_button.configure(state=tk.DISABLED)
    export_ae_button.configure(state=tk.DISABLED)
    export_s_button.configure(state=tk.DISABLED)
    capture_sleep_btn_3.configure(state=tk.DISABLED)
    
    psu_combo_box.configure(state=tk.NORMAL)
    trigger_box.config(state=tk.NORMAL)
    battery_type_combo_box.configure(state=tk.NORMAL)
    battery_cells_combo_box.configure(state=tk.NORMAL)

    cmd = 'y' #turn off trigger interrupt and stop transmitting
    bytes_returned = ser.write(cmd.encode())
    time.sleep(0.1)

    cmd = 'i' #turn voltage off
    bytes_returned = ser.write(cmd.encode())
    time.sleep(0.1)    

    #Reboot the MSP430
    ser.reset_input_buffer()
    cmd = 'p'
    bytes_returned = ser.write(cmd.encode())
    version.set(ser.readline(2).hex())
    if int(version.get(),16) > 1002:
       cmd = 'w'
       bytes_returned = ser.write(cmd.encode())
       time.sleep(0.5)

    p_rad.configure(value=1,foreground='black',background='dark gray')
    p_rad.deselect()
    p_rad1.configure(value=0,foreground='red',background='dark gray')
    p_rad1.select()

    trig_PSU_var.set(0)

    capture_active_event_button.config(text = 'Capture Active' , foreground = 'black')

    #offset = 0
    x[:] = []
    y[:] = []
    s_x[:] = []
    s_y[:] = []
    si[:] = []

    ax.plot(x, y)
    ax.cla()
    plt.close('all')

    axs.plot(x, y)
    axs.cla()
    plt.close('all')

    progress_label.configure(text='',background='dark gray')
    progress_label_s.configure(text='',background='dark gray')
    trig_var.set(0)
    sense_persist_var.set(0)
    plot_active_var.set(0)
    
    data_plot(x,y,str(0),str(0),str(0),str(0),str(0),'Active')
    
    ae_captured_average_current_2 = 0
    sl_captured_average_current_3 = 0
    ae_captured_duration_2 = 0
    soc_state = 0
    
    #Clear all of the Labels and Entry Fields
    ae_captured_current_label_4.configure(text='-',background='dark gray')
    ae_captured_duration_label_4.configure(text='-',background='dark gray')
    sl_captured_current_label_4.configure(text='-',background='dark gray')
    sl_captured_duration_label_4.configure(text='-',background='dark gray')
    dut_cutoff_captured_label_4.configure(text='-',background='dark gray')
    batt_cap_captured_label_4.configure(text='-',background='dark gray')
    average_current_profile_captured_label_4.configure(text='-',background='dark gray')
    captured_battery_life_hours_graph.configure(text='-',background='dark gray')
    captured_battery_life_days_graph.configure(text='-',background='dark gray')
  
    use_range_select_button.configure(state=tk.DISABLED)
    sl_use_range_select_button.configure(state=tk.DISABLED)
    #override_dut_cuttoff_var.set(0)
    #override_dut_cuttoff.configure(state=tk.DISABLED)

    ae_optimized_current_entry_4.delete(0,END)
    ae_optimized_duration_entry_4.delete(0,END)
    dut_cutoff_optimized_entry_4.delete(0,END)
    batt_cap_optimized_entry_4.delete(0,END)
    sl_optimized_current_entry_4.delete(0,END)
    sl_optimized_duration_entry_4.delete(0,END)
    sl_optimized_current_entry_4.delete(0,END)
    sl_optimized_duration_entry_4.delete(0,END)
    select_current_range_entry_1.delete(0,END)
    select_duration_range_entry_1.delete(0,END)
    
    average_current_profile_optimized_label_4.configure(text='-')
    optimized_battery_life_hours_graph.configure(text='-')
    optimized_battery_life_days_graph.configure(text='-')

    average_current_profile_data.configure(text='-')
    max_data.configure(text='-')
    min_data.configure(text='-')
    sl_average_current_profile_data.configure(text='-')
    sl_max_data.configure(text='-')
    sl_min_data.configure(text='-')
    
    avg_active_event_I_2.configure(text='0.00', foreground = 'black')
    avg_active_event_I_units.configure(foreground = 'black')
    avg_sleep_event_I.configure(text='000.00', foreground = 'black')
    avg_sleep_event_I_units.configure(foreground = 'black')

    reset_button = tk.Button(profile_frame,text='Reset',command=reset,state=tk.DISABLED)
   
#################################################################################
###    SETUP LABELS AND BUTTONS
#################################################################################

headerFont = font.Font(family="TkDefaultFont",size=9,underline=1)
headerFont2 = font.Font(family="TkDefaultFont",size=9,underline=1)

# STEP 1 - INPUT BATTERY INFO & PSU OUTPUT
#Battery Information
battery_type_label_1 = Label(profile_frame, text='Battery Type',background='dark gray')
battery_type_label_1.grid(row=1, column=0, padx=10,pady=0,sticky = 'w')
batt_chem = tk.StringVar()
battery_type_combo_box = ttk.Combobox(profile_frame, width=16, textvariable=batt_chem)
battery_type_combo_box['values'] = ('AA-Alkaline', 'AAA-Alkaline', 'LI-Ion','LiFePO4','AA-NiMH/NiCd', 'AAA-NiMH/NiCd',\
   'CR2032','CR123','CR1632','CR2450') 
battery_type_combo_box.grid(row=1, column=0,padx=(150,4),pady=(1,1),sticky = 'w')
battery_type_combo_box.current(0)
battery_type_combo_box.bind('<<ComboboxSelected>>', set_profile_params)

battery_cells = Label(profile_frame, text='Number of Cells',background='dark gray')
battery_cells.grid(row=2, column=0, padx=10,pady=(1,1),sticky = 'w')
batt_cells = tk.StringVar()
battery_cells_combo_box = ttk.Combobox(profile_frame, width=3, textvariable=batt_cells)
battery_cells_combo_box['values'] = (1, 2, 3) 
battery_cells_combo_box.grid(row=2, column=0,padx=(150,4),pady=(1,1),sticky = 'w')
battery_cells_combo_box.current(0)
battery_cells_combo_box.bind('<<ComboboxSelected>>', set_profile_params)
battery_cells_units = Label(profile_frame, text='cells',background='dark gray')
battery_cells_units.grid(row=2, column=0, padx=(190,4),pady=(1,1),sticky = 'w')

battery_capacity_label_1 = Label(profile_frame, text='Battery Capacity (1 cell)',background='dark gray')
battery_capacity_label_1.grid(row=3, column=0, padx=10,pady=0,sticky = 'w')
batt_cap = tk.StringVar()
battery_capactity_entry_1 = Entry(profile_frame, width=6,textvariable=batt_cap)
battery_capactity_entry_1.grid(row=3, column=0, padx=(150,4),pady=(1,1), sticky = 'w')
battery_capactity_entry_1.focus_set()
battery_capactity_entry_1.insert(0,1500)
battery_capactity_units = Label(profile_frame, text='mAh',background='dark gray')
battery_capactity_units.grid(row=3, column=0, padx=(190,4),pady=(1,1),sticky = 'w')
  
#Voltage
dut_cutoff_voltage = Label(profile_frame, text='DUT Cutoff Voltage',background='dark gray')
dut_cutoff_voltage.grid(row=4, column=0, padx=10,pady=(1,1),sticky = 'w')
dut_cutoff = tk.StringVar()
dut_cutoff_voltage_entry = Entry(profile_frame, width=6, textvariable = dut_cutoff)
dut_cutoff_voltage_entry.grid(row=4, column=0, padx=(150,4),pady=(1,1), sticky = 'w')
dut_cutoff_voltage_entry.insert(0,1.0)
dut_cutoff_voltage_entry.bind('<Return>', update_soc_chart)
dut_cutoff_voltage_entry.bind('<FocusOut>', update_soc_chart)
dut_cutoff_voltage_entry.focus_set()
dut_cutoff_voltage_units = Label(profile_frame, text='volts',background='dark gray')
dut_cutoff_voltage_units.grid(row=4, column=0, padx=(190,4),pady=(1,1),sticky = 'w')

volt_lab = Label(profile_frame, text='PSU Voltage Output',background='dark gray')
volt_lab.grid(row=5, column=0, padx=10,pady=(1,1),sticky = 'w')
voltage = tk.StringVar()
psu_combo_box = ttk.Combobox(profile_frame, width=3, textvariable=voltage)
psu_combo_box['values'] = (1.2, 1.5, 2.4, 3.0, 3.2, 3.6, 3.7, 4.2, 4.5) 
psu_combo_box.grid(row=5, column=0,padx=(150,4),pady=(1,1),sticky = 'w')
psu_combo_box.current(1)
psu_combo_box_units = Label(profile_frame, text='volts',background='dark gray')
psu_combo_box_units.grid(row=5, column=0, padx=(190,4),pady=(1,1),sticky = 'w')
voltage.set('1.5')
psu_lab = Label(profile_frame, text='PSU Output',background='dark gray')
psu_lab.grid(row=6, column=0, padx=10,pady=(1,1),sticky = 'w')

def psu_off():
   p_rad.configure(foreground='black',background='dark gray')
   p_rad1.configure(foreground='red',background='dark gray')
   cmd = 'i'
   bytes_returned = ser.write(cmd.encode())
   
p_radio = IntVar()
p_rad = Radiobutton(profile_frame, text = 'On', variable = p_radio, value = 1,
                    command = set_battery_voltage,background='dark gray')
p_rad.grid(row=6, column=0, padx=80, pady=(1,1),sticky = 'w')

p_rad1 = Radiobutton(profile_frame, text = 'Off', variable = p_radio, value = 0, command = psu_off,
                     foreground='red',background='dark gray')
p_rad1.grid(row=6, column=0, padx=(120,10),pady=(1,1), sticky = 'w')

trig_PSU_var = IntVar()
trigger_box = tk.Checkbutton(profile_frame, text='Trigger PSU on Capture', variable=trig_PSU_var, background='dark gray', state=tk.NORMAL)
trigger_box.grid(row=6, column=0, padx=(160,4),pady=(1,1),sticky='w')
trig_PSU_var.set(0)

#STEP2 - SET UP CAPTURE TIME AND EXECUTE CAPTURE

progress_label = ttk.Label(profile_frame, text='',background='dark gray')
progress_label.grid(row=7, column = 0, padx=(230,4),sticky='w')

rt_c = Label(profile_frame, text='DUT Active Duration',background='dark gray')
rt_c.grid(row=8, column=0, padx=8,pady=(1,1),sticky = 'w')
sl_duration_units_lab_3 = Label(profile_frame, text='Sec',background='dark gray')
sl_duration_units_lab_3.grid(row=8, column=0, padx=(160,2),pady=(1,1),sticky = 'w')
runtime_duration = tk.StringVar()
rt_dur = Entry(profile_frame, width=6,textvariable=runtime_duration)
rt_dur.grid(row=8, column=0, padx=(120,4),pady=(1,1), sticky = 'w')
rt_dur.focus_set()
rt_dur.insert(0,10)
rt_dur.configure(state=tk.NORMAL)

choice_lab = Label(profile_frame, text=' -OR- ',background='dark gray')
choice_lab.grid(row=8, column=0, padx=(185,2),pady=(1,1),sticky = 'w')

trig_var = IntVar()
trigger_box = tk.Checkbutton(profile_frame, text='Ext Trig', variable=trig_var,command = TrigArmed,background='dark gray', state=tk.NORMAL)
trigger_box.grid(row=8, column=0, padx=(225,4),pady=(1,1),sticky='w')
   
capture_active_event_button = tk.Button(profile_frame,text='Capture Active',command=capture_profile,state=tk.NORMAL)
capture_active_event_button.grid(row=9,column=0, padx=(10,4),pady=(1,1),sticky = 'w')
avg_active_event_I_2 = ttk.Label(profile_frame, text='0.00',font=('Arial Bold',10), foreground = 'black',background='dark gray',state=tk.NORMAL)
avg_active_event_I_2.grid(row=9, column = 0, padx= (120,4),pady=(1,1), sticky = 'w')
avg_active_event_I_units = ttk.Label(profile_frame, text='mA',font=('Arial Bold',10), foreground = 'black',background='dark gray',state=tk.NORMAL)
avg_active_event_I_units.grid(row=9, column = 0, padx=(170,4),pady=(1,1), sticky = 'w')

plot_active_var = IntVar()
active_plot = tk.Checkbutton(profile_frame, text='Only Active Plot', variable=plot_active_var,background='dark gray', state=tk.NORMAL)
active_plot.grid(row=9, column=0, padx=(225,4),pady=(1,1),sticky='w')

#STEP3 - CAPTURE SLEEP EVENT CURRENT WIDGETS

progress_label_s = ttk.Label(profile_frame, text='',background='dark gray')
progress_label_s.grid(row=10, column = 0, padx=(230,4),sticky='w')

sl_duration_labe1_3 = Label(profile_frame, text='DUT Sleep Duration',background='dark gray')
sl_duration_labe1_3.grid(row=11, column=0, padx=10,pady=(1,1),sticky = 'w')
sleep_duration=tk.StringVar()
sl_duration_entry_3 = Entry(profile_frame, width=6,textvariable=sleep_duration)
sl_duration_entry_3.grid(row=11, column=0,padx=(120,4),pady=(1,1),sticky = 'w')
sl_duration_entry_3.insert(0,60)
sl_duration_entry_3.configure(state=tk.NORMAL)
sl_duration_units_lab_3 = Label(profile_frame, text='Sec',background='dark gray')
sl_duration_units_lab_3.grid(row=11, column=0, padx=(160,2),pady=(1,1),sticky = 'w')

sl_range_labe1_3 = Label(profile_frame, text='Sleep Current Range',background='dark gray')
sl_range_labe1_3.grid(row=11, column=0, padx=(195,2) ,pady=(1,1),sticky = 'w')

def sl_select_shunt(eventObject):
   if (sl_shunt_var.get() == '800uA - 500mA'):
      #Turn OFF low current sense resistor
      cmd = 'l'
      bytes_returned = ser.write(cmd.encode())
   
   elif (sl_shunt_var.get() == '10uA - 800uA'):
      #Turn ON low current sense resistor
      cmd = 'k'
      bytes_returned = ser.write(cmd.encode())
   else:
      manual_sleep_msg()

sl_shunt_var = tk.StringVar()
sl_shunt_select__combo_box = ttk.Combobox(profile_frame, width=14, textvariable=sl_shunt_var)
sl_shunt_select__combo_box['values'] = ('800uA - 500mA', '10uA - 800uA') 
sl_shunt_select__combo_box.grid(row=12,column=0,padx=(195,4),pady=(1,1),sticky='w')
sl_shunt_select__combo_box.current(0)
sl_shunt_var.set('800uA - 500mA')
sl_shunt_select__combo_box.bind('<<ComboboxSelected>>', sl_select_shunt)

capture_sleep_btn_3 = tk.Button(profile_frame,text='Capture Sleep',command=capture_sleep_profile,state=tk.DISABLED)
capture_sleep_btn_3.grid(row=12,column=0, padx=(10,4),pady=(1,1),sticky = 'w')

avg_sleep_event_I = ttk.Label(profile_frame, text='0000',font=('Arial Bold',10), foreground = 'black',background='dark gray',state=tk.NORMAL)
avg_sleep_event_I.grid(row=12, column = 0, padx= (120,4),pady=(1,1), sticky = 'w')

avg_sleep_event_I_units = ttk.Label(profile_frame, text='uA',font=('Arial Bold',10), foreground = 'black',background='dark gray')
avg_sleep_event_I_units.grid(row=12, column = 0, padx=(170,4),pady=(1,1), sticky = 'w')

sense_persist_var = IntVar()
persist_box = tk.Checkbutton(profile_frame, text='Persist Sense Resistor', variable=sense_persist_var,background='dark gray', state=tk.NORMAL)
persist_box.grid(row=13, column=0, padx=(190,4),pady=(1,1),sticky='w')

#STEP4 - RESULTS AND OPTIMIZE  WIDGETS
#Section 4 Fields

#Profile Headers
captured_profile_label = ttk.Label(profile_frame, text='Captured' ,font=headerFont,foreground='blue',background='dark gray')
captured_profile_label.grid(row=15, column = 0, padx=(170,4),pady=(1,1),sticky = 'w')
optimized_profile_label = Label(profile_frame, text='Optimized',foreground='blue',font=headerFont,background='dark gray')
optimized_profile_label.grid(row=15, column=0, padx=(250,1),pady=(1,1),sticky = 'w')

#Active Event Current
ae_current_label_4 = Label(profile_frame, text='Active Event Current',background='dark gray')
ae_current_label_4.grid(row=16, column=0, padx=10,pady=(1,1),sticky = 'w')
ae_captured_current_label_4 = Label(profile_frame, text='-', background='dark gray')
ae_captured_current_label_4.grid(row=16, column=0, padx=(180,4),pady=(1,1),sticky = 'w')
ae_optimized_current_entry_4 = Entry(profile_frame, width=7)
ae_optimized_current_entry_4.grid(row=16, column=0,padx=(260,4),pady=(1,1),sticky = 'w')
ae_current_units_lab_4 = Label(profile_frame, text='mA',background='dark gray')
ae_current_units_lab_4.grid(row=16, column=0, padx=(320,2),pady=(1,1),sticky = 'w')

#Active Event Duration
ae_duration_label_4 = Label(profile_frame, text='Active Event Duration',background='dark gray')
ae_duration_label_4.grid(row=17, column=0, padx=10,pady=4,sticky = 'w')
ae_captured_duration_label_4 = Label(profile_frame, text='-',background='dark gray')
ae_captured_duration_label_4.grid(row=17, column=0, padx=(180,4),pady=(1,1),sticky = 'w')
ae_optimized_duration_entry_4 = Entry(profile_frame, width=7)
ae_optimized_duration_entry_4.grid(row=17, column=0,padx=(260,4),pady=(1,1),sticky = 'w')
ae_duration_units_lab_4 = Label(profile_frame, text='S',background='dark gray')
ae_duration_units_lab_4.grid(row=17, column=0, padx=(320,2),pady=(1,1),sticky = 'w')

#Sleep Event Current
sl_current_label_4 = Label(profile_frame, text='Sleep Current',background='dark gray')
sl_current_label_4.grid(row=18, column=0, padx=10,pady=(1,1),sticky = 'w')
sl_captured_current_label_4 = Label(profile_frame, text='-',background='dark gray')
sl_captured_current_label_4.grid(row=18, column=0, padx=(180,4),pady=(1,1),sticky = 'w')
sl_optimized_current_entry_4 = Entry(profile_frame, width=7)
sl_optimized_current_entry_4.grid(row=18, column=0,padx=(260,4),pady=(1,1),sticky = 'w')
sl_current_units_lab_4 = Label(profile_frame, text='mA',background='dark gray')
sl_current_units_lab_4.grid(row=18, column=0, padx=(320,2),pady=(1,1),sticky = 'w')

#Sleep Event Duration
sl_duration_labe1_4 = Label(profile_frame, text='Sleep Duration',background='dark gray')
sl_duration_labe1_4.grid(row=19, column=0, padx=10,pady=(1,1),sticky = 'w')
sl_captured_duration_label_4 = Label(profile_frame, text='-',background='dark gray')
sl_captured_duration_label_4.grid(row=19, column=0, padx=(180,4),pady=(1,1),sticky = 'w')
sl_optimized_duration_entry_4 = Entry(profile_frame, width=7)
sl_optimized_duration_entry_4.grid(row=19, column=0,padx=(260,4),pady=(1,1),sticky = 'w')
sl_duration_units_lab_4 = Label(profile_frame, text='S',background='dark gray')
sl_duration_units_lab_4.grid(row=19, column=0, padx=(320,2),pady=(1,1),sticky = 'w')
      
#DUT Cutoff Voltage
dut_cutoff_label_4 = Label(profile_frame, text='DUT Cutoff Voltage',background='dark gray')
dut_cutoff_label_4.grid(row=20, column=0, padx=10,pady=(1,1),sticky = 'w')
dut_cutoff_captured_label_4 = Label(profile_frame, text='-',background='dark gray')
dut_cutoff_captured_label_4.grid(row=20, column=0, padx=(180,4),pady=(1,1),sticky = 'w')
dut_cutoff_optimized_entry_4 = Entry(profile_frame, width=7)
dut_cutoff_optimized_entry_4.grid(row=20, column=0, padx=(260,4),pady=(1,1), sticky = 'w')
dut_cutoff_units_lab_4 = Label(profile_frame, text='volts',background='dark gray')
dut_cutoff_units_lab_4.grid(row=20, column=0,  padx=(320,2),pady=(1,1),sticky = 'w')

#Battery Capacity
batt_cap_label_4 = Label(profile_frame, text='Effective Battery Capacity',background='dark gray')
batt_cap_label_4.grid(row=21, column=0,  padx=10,pady=(1,1),sticky = 'w')
batt_cap_captured_label_4 = Label(profile_frame, text='-',background='dark gray')
batt_cap_captured_label_4.grid(row=21, column=0, padx=(180,4),pady=(1,1),sticky = 'w')
batt_cap_optimized_entry_4 = Entry(profile_frame, width=7)
batt_cap_optimized_entry_4.grid(row=21, column=0,  padx=(260,4),pady=(1,1), sticky = 'w')
batt_cap_units_lab_4 = Label(profile_frame, text='mAh',background='dark gray')
batt_cap_units_lab_4.grid(row=21, column=0,  padx=(320,2),pady=(1,1),sticky = 'w')

override_dut_cuttoff_var = IntVar()
override_dut_cuttoff = tk.Checkbutton(profile_frame, text='Overide DUT Cutoff', variable=override_dut_cuttoff_var,background='dark gray', state=tk.NORMAL)
override_dut_cuttoff.grid(row=21, column=0,columnspan=3, padx=(350,4),pady=(1,1),sticky='w')

#Average Current Profile
average_current_profile_label_4 = Label(profile_frame, text='Average Current Profile',background='dark gray')
average_current_profile_label_4.grid(row=22, column=0, padx=10,pady=(1,1),sticky = 'w')
average_current_profile_captured_label_4 = Label(profile_frame, text='-',background='dark gray')
average_current_profile_captured_label_4.grid(row=22, column=0, padx=(180,4),pady=(1,1),sticky = 'w')
average_current_profile_optimized_label_4 = Label(profile_frame, text='-',foreground='black', background='dark gray')
average_current_profile_optimized_label_4.grid(row=22, column=0, padx=(260,4),pady=(1,1),sticky = 'w')
average_current_profile_units_lab_4 = Label(profile_frame, text='mA',foreground='black',background='dark gray')
average_current_profile_units_lab_4.grid(row=22, column=0,padx=(320,2),pady=(1,1),sticky = 'w')

#Select Active Current Region
def replace_active():
   u = 0
   try:
      ae_optimized_current_entry_4.delete(0,END)
      ae_optimized_current_entry_4.insert(0,str(round(float(select_current_range_entry_1.get()),3)))
      ae_optimized_duration_entry_4.delete(0,END)
      ae_optimized_duration_entry_4.insert(0,str(round(float(select_duration_range_entry_1.get())/1000,3)))
   except:
      u=u+1

def replace_sleep():
   u = 0
   
   try:
      sl_optimized_current_entry_4.delete(0,END)
      sl_optimized_current_entry_4.insert(0,str(round(float(select_current_range_entry_1.get()),3)))
      sl_optimized_duration_entry_4.delete(0,END)
      sl_optimized_duration_entry_4.insert(0,str(round(float(select_duration_range_entry_1.get())/1000,3)))
   except:
      u=u+1  

select_current_entry_1_label1 = Label(profile_frame, text='I(mA)')
select_current_entry_1_label1.grid(row=19, column=1, padx=(440,4),pady=(1,1),sticky = 'w')
select_current_range_entry_1 = Entry(profile_frame, width=8)
select_current_range_entry_1.grid(row=19, column=1, padx=(480,4),pady=(8,8), sticky = 'w')
select_current_entry_1_label2 = Label(profile_frame, text='Dur(mS)')
select_current_entry_1_label2.grid(row=19, column=1, padx=(530,4),pady=(1,1),sticky = 'w')
select_duration_range_entry_1 = Entry(profile_frame, width=8)
select_duration_range_entry_1.grid(row=19, column=1, padx=(580,4),pady=(8,8), sticky = 'w')
use_range_select_button = tk.Button(profile_frame, text='Capture Active', command=replace_active, state=tk.DISABLED)
use_range_select_button.grid(row=19, column=1,columnspan=3,padx=(640,4),pady=(8,8),sticky='w')
sl_use_range_select_button = tk.Button(profile_frame, text='Capture Sleep', command=replace_sleep, state=tk.DISABLED)
sl_use_range_select_button.grid(row=19, column=1,columnspan=3,padx=(730,2),pady=(8,8),sticky='w')

#Statistics
statistics_label = Label(profile_frame, font=headerFont,text='Statistics',foreground='blue',background='dark gray')
statistics_label.grid(row=23, column=1, columnspan=2,padx=90,pady=(1,1),sticky = 'w')
ae_statistics_label = Label(profile_frame, font=headerFont,text='Active Event',foreground='blue',background='dark gray')
ae_statistics_label.grid(row=23, column=1, padx=220,pady=(1,1),sticky = 'w')
sl_statistics_label = Label(profile_frame, font=headerFont,text='Sleep Event',foreground='blue',background='dark gray')
sl_statistics_label.grid(row=23, column=1, padx=300,pady=(1,1),sticky = 'w')
average_current_profile = Label(profile_frame, text='Average Current',background='dark gray')
average_current_profile.grid(row=24, column=1, padx=90,pady=(1,1),sticky = 'w')
average_current_profile_data = Label(profile_frame, text='-',background='dark gray')
average_current_profile_data.grid(row=24, column=1, padx=(240,2),pady=(1,1),sticky = 'w')
sl_average_current_profile_data = Label(profile_frame, text='-',background='dark gray')
sl_average_current_profile_data.grid(row=24, column=1, padx=(320,2),pady=(1,1),sticky = 'w')
max_label = ttk.Label(profile_frame, text='Max current',background='dark gray')
max_label.grid(row=25, column = 1, rowspan=1, padx=90,pady=(2,2),sticky = 'w')
max_data = Label(profile_frame, text='-',background='dark gray')
max_data.grid(row=25, column=1,  rowspan=1,padx=(240,2),pady=(2,2),sticky = 'w')
sl_max_data = Label(profile_frame, text='-',background='dark gray')
sl_max_data.grid(row=25, column=1,  rowspan=1,padx=(320,2),pady=(2,2),sticky = 'w')
min_label = ttk.Label(profile_frame, text='Min current',background='dark gray')
min_label.grid(row=26, column = 1,padx=90,pady=(2,2),sticky = 'w')
min_data = Label(profile_frame, text='-',background='dark gray')
min_data.grid(row=26,column=1,padx=(240,2),pady=(2,2),sticky = 'w')
sl_min_data = Label(profile_frame, text='-',background='dark gray')
sl_min_data.grid(row=26,column=1,padx=(320,2),pady=(2,2),sticky = 'w')

average_current_profile_units = Label(profile_frame, text='mA',background='dark gray')
average_current_profile_units.grid(row=24, column=1, padx=(380,2),pady=(1,1),sticky = 'w')
max_units = Label(profile_frame, text='mA',background='dark gray')
max_units.grid(row=25, column=1, padx=(380,2),pady=(1,1),sticky = 'w')
min_units = Label(profile_frame, text='mA',background='dark gray')
min_units.grid(row=26, column=1, padx=(380,2),pady=(1,1),sticky = 'w')

#Battery Life Profile Headers
#captured_profile_label1 = ttk.Label(profile_frame, text='Captured' ,foreground='blue',background='dark gray',font=headerFont2)
#captured_profile_label1.grid(row=24, column = 0, padx=(100,4),pady=(1,1),sticky = 'w')

#optimized_profile_label1 = Label(profile_frame, text='Optimized',foreground='blue',background='dark gray',font=headerFont2)
#optimized_profile_label1.grid(row=24, column=0, padx=(200,1),pady=(1,1),sticky = 'w')

#Battery Life Hours
batt_life_hours_captured_graph_label = ttk.Label(profile_frame, text='Estimated Battery Life',foreground = 'blue',background='dark gray',font=("TkDefaultFont", 9))
batt_life_hours_captured_graph_label.grid(row=23, column=0, padx=10,pady=(1,1), sticky = 'w')
captured_battery_life_hours_graph = ttk.Label(profile_frame, text='-',foreground='blue',background='dark gray',font=("TkDefaultFont", 9))
captured_battery_life_hours_graph.grid(row=23, column = 0,padx=(180,4),pady=(1,1),sticky = 'w')
optimized_battery_life_hours_graph = ttk.Label(profile_frame, text='-',foreground='blue',background='dark gray',font=("TkDefaultFont", 9))
optimized_battery_life_hours_graph.grid(row=23, column = 0,padx=(260,4),pady=(1,1),sticky = 'w')
optimized_battery_life_hours_units_lab_4 = Label(profile_frame, text='hours',foreground = 'blue',background='dark gray')
optimized_battery_life_hours_units_lab_4.grid(row=23, column=0,padx=(320,2),pady=(1,1),sticky = 'w')

#Battery Life Days
batt_life_days_captured_graph_label = ttk.Label(profile_frame, text='Estimated Battery Life', foreground = 'blue',background='dark gray',font=("TkDefaultFont", 9))
batt_life_days_captured_graph_label.grid(row=24, column = 0,padx=10,pady=(1,1),sticky = 'w')
captured_battery_life_days_graph = ttk.Label(profile_frame, text='-' ,foreground='blue',background='dark gray',font=("TkDefaultFont", 9))
captured_battery_life_days_graph.grid(row=24, column = 0,padx=(180,4),pady=(1,1),sticky = 'w')
optimized_battery_life_days_graph = ttk.Label(profile_frame, text='-',foreground='blue',background='dark gray',font=("TkDefaultFont", 9))
optimized_battery_life_days_graph.grid(row=24, column = 0,padx=(260,4),pady=(1,1),sticky = 'w')
optimized_battery_life_days_units_lab_4 = Label(profile_frame, text='days',foreground = 'blue',background='dark gray')
optimized_battery_life_days_units_lab_4.grid(row=24, column=0,padx=(320,2),pady=(1,1),sticky = 'w')

#OPTIMIZE BUTTON

##RESET BUTTON
reset_button = tk.Button(profile_frame,text='Reset  ',command=reset,state=tk.NORMAL)
reset_button.grid(row=25,column=0,padx=(180,4),pady=(1,1),sticky = 'nw')

optimize_button = tk.Button(profile_frame,text='Optimize',command=optimize_profile,state=tk.NORMAL)
optimize_button.grid(row=25,column=0, padx=(260,4),pady=(1,1),sticky = 'nw')

##SAVE BUTTON
save_button = tk.Button(profile_frame,text='Save Results',command=SaveFile,state=tk.DISABLED)
save_button.grid(row=26,column=0,padx=(80,4),pady=(1,1),sticky = 'sw')

##EXPORT DATA BUTTON
export_ae_button = tk.Button(profile_frame,text='Export Active Data',command=export_ae_data,state=tk.DISABLED)
export_ae_button.grid(row=26,column=0,padx=(157,4),pady=(1,1),sticky = 'sw')

export_s_button = tk.Button(profile_frame,text='Export Sleep Data',command=export_s_data,state=tk.DISABLED)
export_s_button.grid(row=26,column=0,padx=(268,4),pady=(1,1),sticky = 'sw')

#STEP LABELS
step1_label = ttk.Label(profile_frame, text='Step1 - Battery Info and PSU Output',font=('Arial Bold',11), foreground = 'blue',background='dark gray')
step1_label.grid(row=0, column = 0, padx=2,pady=(1,1), sticky = 'w',columnspan=2)

step2_label = ttk.Label(profile_frame, text='Step2 - Active Event Current',font=('Arial Bold',11), background='dark gray')
step2_label.grid(row=7, column = 0, padx=2,pady=(1,1),sticky = 'w',columnspan=2)

step3_label = ttk.Label(profile_frame, text='Step3 - Sleep Event Current',font=('Arial Bold',11), background='dark gray')
step3_label.grid(row=10, column = 0, padx=2, pady=(1,1), sticky = 'w')

step4_label = ttk.Label(profile_frame, text='Step4 - Results and Optimization',font=('Arial Bold',11), background='dark gray')
step4_label.grid(row=14, column = 0, padx=2, pady=(1,1), sticky = 'w')

update_soc_chart(0)
data_plot(x,y,str(0),str(0),str(0),str(0),str(0),'Active')
#cmd = 'i' #turn voltage off
#bytes_returned = ser.write(cmd.encode())

root.protocol("WM_DELETE_WINDOW", lambda arg=root: quitapp(arg))
root.mainloop()

