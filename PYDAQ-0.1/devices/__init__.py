
from os.path import dirname, basename, isfile
import glob
#import tkSimpleDialog
#import Tkinter as tkinter
#from Tkconstants import BOTH, TOP
import gui
from gui.terminator import terminatehooks


devices=[]
last_selected_device=None
active_device=None
plot=None


class DeviceBase(object):
    """
    Baseclass for devices.
    """
    options=[
             # sth. like {'name','type','values'}
             ]
    def __init__(self):
        """
        Instanciate a device.
        """
        self.enabled=0
        self.record=None
    def read(self):
        """
        Receive some date from the device
        """
    def dialog(self,master):
        """
        This method must return a QT-Frame with controls for the device's properties.
        """
    def dialog_ok(self):
        """
        trigger for the OK-button. This method sets the properties and should start a workerthread \
        who receives and processes incoming data
        """
    def _enable(self):
        self.enabled=1
        self.enable()
    def enable(self):
        """
        a method mich enables and or starts the workerthread
        """
    def _disable(self):
        self.enabled=0
        self.disable()
    def disable(self):
        """
        A method which disables the workerthread
        """
    def record(self,file):
        pass
    def get_settings(self):
        """
        returns a dict with the current settings of the device
        """
    def set_settings(self,data):
        """
        Apply settings of the dict a (as saved by @ref:self.get_settings) to the device
        @param data: a dict containing the settings
        """
        
#from devices import *
#import DataGen







def save_devices():
    """
    Save data to disk as retured by device.get_settings(). 
    """
    from pickle import dump
    f=open('sav','w')
    data={}
    for dev in devices:
        data[dev.name]=dev.get_settings()
    print "saving data", data
    dump(data, f)
    f.close()
def restore_settings():
    """
    Load data from disk and restore device data
    """
    from pickle import load
    f=None
    try: 
        f=open('sav')
        data=load(f)
    except (IOError,EOFError): 
        print "error loading data. Using defaults."
        return
    f.close()
    for dev in devices:
        try: dev.set_settings(data[dev.name])
        except KeyError: pass
def stop_devices():
    '''
    Stop all devices
    '''
    for d in devices:
        d.disable()

def init_devices():
    """
    Import all files in this folder.
    """
    #from . import *
    modules = glob.glob(dirname(__file__)+"/*.py")
    modules = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
    print __name__,modules
    for m in modules:__import__(m,globals())
    
    terminatehooks.append(save_devices)
    terminatehooks.append(stop_devices)
    restore_settings()
# 
# class DevicesDialog(tkSimpleDialog.Dialog):
# 
#     def selDevice(self,ev):
#         print ev
#         #find the right device
#         for d in devices:
#             if d.name==ev: 
#                 assert isinstance(d, DeviceBase)
#                 for child in self.dev_frame.winfo_children():child.destroy()
#                 d.dialog(self.dev_frame)
#                 self.selected_device=d
#                 
#                 
#         pass
#     def body(self, master):
#         self.applied=0
#         opts=[d.name for d in devices]
#         tkSimpleDialog.Dialog.body(self, master)
#         self.selected_device=last_selected_device or devices[0]
#         drop_frame=tkinter.Frame(master,width=200,height=20)
#         #drop_frame.pack_propagate(0)
#         drop_frame.pack(side='left')
#         
#         var1 = tkinter.StringVar(value=self.selected_device.name)
#         drop = tkinter.OptionMenu(drop_frame,var1,*opts,command=self.selDevice)
#         drop.config(width=10)
#         drop.pack(side='left',expand=1,fill=BOTH)
#         
#         self.dev_frame=tkinter.Frame(master,width=500,height=400)
#         self.dev_frame.config(width=300,height=200)
#         #self.dev_frame.grid_propagate(0)
#         self.dev_frame.pack(side='right',expand=1,fill=BOTH)
#         #label=tkinter.Label(dev_frame,text="Please Select a Device")
#         #label.pack(fill=BOTH,anchor='n')
#         self.dev_frame.master=self
#         #Create Device Dialoag after MainDialog is complete
#         self.after_idle(self.selected_device.dialog,self.dev_frame)
#         #self.selected_device.dialog(self.dev_frame)
#     def apply(self):
#         global last_selected_device,active_device
#         tkSimpleDialog.Dialog.apply(self)
#         self.selected_device.dialog_ok()
#         active_device=self.selected_device
#         last_selected_device=self.selected_device
#         self.applied=1