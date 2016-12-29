'''
Created on 24.11.2016

@author: simon
'''
from devices import DeviceBase,devices
import pyaudio,threading,time,warnings
from gui.terminator import terminatehooks


SRATES=[44100,48000,64000,88200,96000,144000,192000]
class AudioDevice(DeviceBase):
    name="Audio IO"
    description="""
    Get data from audio inputs
    """
    def __init__(self):
        self.selectedDevice=None
        self.inputdevices=[]
        self.srate=None,
        self.channels=None
        DeviceBase.__init__(self)
        terminatehooks.append(self._disable)
    
    def run(self):
        """
        The run-method of  the data-acquisition thread
        """
        from devices import plot
        from gui.plot2 import Plot
        import struct,numpy as np
        plt=plot
        assert isinstance(plt, Plot)
        plt.initplot()

        
        FORMAT = pyaudio.paInt16
        CHANNELS = self.channels
        RATE = self.srate
        CHUNK = min(RATE/30,1024)
        plt.samplerate=RATE
        p = pyaudio.PyAudio()
        #for i in range(p.get_device_count()): print p.get_device_info_by_index(i)
        [plt.pltAddLine() for i in range(CHANNELS)]
        plt.selectedlines=set(plt.lines)
        
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=self.selectedDevice['index'])

        scnt=0
        fcnt=0
        st=time.time()
        while self.enabled:
            #print "sdfg"
            try: 
                data=stream.read(CHUNK)
                #vals=np.empty(CHUNK*CHANNELS)
    #             for i in xrange(0, len(data), 2):
    #                 bs=data[i:i+2] 
    #                 val=struct.unpack('h',bs)
    #                 vals[i//2]=(float(val[0]))
                #print len(vals)
                vals=np.fromstring(data,dtype=np.int16)
                vals=vals.reshape(CHANNELS,-1,order='F')
                scnt+=vals.shape[1]
                fcnt+=1
                if plt.terminalEnabled:
                    [plt.addtxt(
                               ','.join(["%+06.0d"%v for v in i])) for i in vals.transpose()[:-1000]]
                               
                if time.time()-st>1:
                    #plt.samplerate=scnt/(time.time()-st)
                    plt.master.statusmsgs['frate']="ts=%d"%(fcnt/(time.time()-st))
                    st=time.time()
                    scnt=0
                    fcnt=0
                    plt.master.statusmsgs['srate']="%d/s"%plt.samplerate
                plt.pltAppendMultiplePointsToLines(vals,align=1)
            except IOError,e: 
                warnings.warn(str(e)) # and ignore futher exceptions
                #print "ioerror:", e.errno
        stream.close()
        print "audiostream closed"
    def dialog(self, master):
        """
        @see: DeviceBase.dialog
        """
        from PyQt4 import QtCore, QtGui
        
        grid=QtGui.QGridLayout()
        frame=QtGui.QFrame(master)
        frame.setLayout(grid)  
        
        wdg=self.devices_wdg=QtGui.QComboBox()
        if not self.inputdevices: self.inputdevices=self.paGetInputs()
        print self.defaultDevice
        for dev in self.inputdevices:
            wdg.addItem(dev['name'])
        wdg.setCurrentIndex(self.inputdevices.index(self.selectedDevice or self.defaultDevice))
        wdg.currentIndexChanged.connect(self.dialog_fill)
        lbl=QtGui.QLabel()
        lbl.setText("Device")
        grid.addWidget(lbl,0,0)
        grid.addWidget(wdg,0,1)        
        
        
        wdg=self.channels_wdg=QtGui.QComboBox()
        lbl=QtGui.QLabel()
        lbl.setText("Channels")
        grid.addWidget(lbl,1,0)
        grid.addWidget(wdg,1,1)
        
        wdg=self.samplerate_wdg=QtGui.QComboBox()
        wdg.setEditable(True)
        lbl=QtGui.QLabel()
        lbl.setText("SampleRate")
        grid.addWidget(lbl,2,0)
        grid.addWidget(wdg,2,1)
        
        self.dialog_fill(self.devices_wdg.currentIndex())
        
        return frame
        
    def dialog_fill(self,ev):
        """ 
        Fill Dialog Fields if device with id ev was selected
        :param (int) ev: Device id 
        """
        
        dev=self.inputdevices[ev]
        print ev,dev
        self.selectedDevice=dev
        self.samplerate_wdg.clear()
        [self.samplerate_wdg.addItem("%d"%i) for i in dev['srates']]
        if self.srate in dev['srates']:
            self.samplerate_wdg.setCurrentIndex(dev['srates'].index(self.srate))
        self.channels_wdg.clear()
        chs=range(1,dev['maxInputChannels']+1)
        [self.channels_wdg.addItem("%d"%i) for i in chs]
        if self.channels in chs:
            self.channels_wdg.setCurrentIndex(chs.index(self.channels))
        
    def dialog_ok(self):
        print "starting audodevice"
        
        self.srate=int(self.samplerate_wdg.currentText())
        self.channels=self.channels_wdg.currentIndex()+1
        
        self.enabled=1
        t=threading.Thread(target=self.run)
        t.daemon=True
        t.start()
    pass

    def paGetInputs(self):
        """
        return a list of all inputs
        :rtype: list a list of all available audio inputs
        """
        devs=[]
        self.defaultDevice=None
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()): 
            devinfo=p.get_device_info_by_index(i)
            if devinfo['name']=="default": self.defaultDevice=devinfo
            
            if devinfo['maxInputChannels']:
                devs.append(devinfo)
                devinfo['srates']=[]
                for i in SRATES:
                    try:
                        if p.is_format_supported(i,  # Sample rate
                                  input_device=devinfo['index'],
                                  input_channels=devinfo['maxInputChannels'],
                                  input_format=pyaudio.paInt16):
                            devinfo['srates'].append(i)
                    except ValueError: pass
        return devs

devices.append(AudioDevice())