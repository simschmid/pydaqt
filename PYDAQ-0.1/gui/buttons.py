'''
Created on 25.10.2016

@author: simon
'''

from Tkinter import *
import gui
import tkFileDialog,time
import traceback
#from devices import DevicesDialog, active_device
import devices
gui.device_started=0

global pauseplay,recdata
def makebuttons(master):
    f=Frame(master)
    f.pack(fill=BOTH,expand=1)
    global pauseplay,recdata
    pauseplay=Button(f,text="Start",command=data_pause_play,width=7)
    pauseplay.pack(side=LEFT)
    
    autozoom=Button(f,text="Auto Zoom",command=gui.pltAutoZoom)
    autozoom.pack(side=LEFT)
    
    savedata=Button(f,text="SaveData",command=save_data)
    savedata.pack(side=LEFT)
    
    recdata=Button(f,text="Record",command=rec_data,width=10)
    recdata.pack(side=LEFT)    
    
    selectgraphs=Button(f,text="Select Lines",command=select_lines)
    selectgraphs.pack(side=RIGHT)    
def data_pause_play():
    
    if not gui.device_started: 
        d=DevicesDialog(gui.top)
        
        if d.applied: 
            gui.device_started^=1
            pauseplay.config(text="Stop")
        d.destroy()
    else: 
        gui.device_started=0
        devices.active_device._disable()
        pauseplay.config(text="Start")
    pass
def save_data():
    
    print tkFileDialog.asksaveasfilename()
    pass

DefaultBGColor=''
def rec_data():
    active_device=devices.active_device
    if not active_device.record:
        types=[("csv","csv")]
        global DefaultBGColor
        DefaultBGColor=recdata.cget('bg')
        filename=tkFileDialog.asksaveasfilename(defaultextension=".csv",initialdir="~",filetypes=types)
        if not filename: return
        recdata.config(text='stop',bg='red')
        active_device.record=open(filename,'w')
        print filename
    else:
        assert isinstance(active_device.record,FileType)
        f=active_device.record
        active_device.record=None
        time.sleep(.1)
        f.close()
        recdata.config(text='Record',bg=DefaultBGColor)

    traceback.print_stack()
def select_lines():
    gui.pltSelectLinesDialog(gui.top)
    pass