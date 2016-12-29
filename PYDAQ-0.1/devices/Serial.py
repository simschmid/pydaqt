'''
Created on 25.10.2016

@author: simon
'''

'''
Created on 24.10.2016

@author: simon
'''
import numpy as np
from devices import  *

import serial,time,parser
import serial.tools.list_ports as lscoms
from collections import deque
from threading import Thread
from gui.terminator import terminatehooks
import traceback

def parsefn(s):
    #from numpy import *
    
    try:
        
        #print s
        s=(   
"""
from numpy import *
#print globals()
def func(x):
    return %s
print func(1)
#end            
"""%s
         )
        exec(s,locals().update(vars(np)))
        #print "fn evals to", func(1)
    except: print traceback.print_exc()
    return func

class Serial(DeviceBase):
    name="Serial"
    def __init__(self,maxlen=0):
        DeviceBase.__init__(self)
        self.maxlen=maxlen
        self.idx=0
        self.serial=serial.Serial()
        #for dev in lscoms.comports():print dev
        self.fnstr="#Recalculate Values. \nx[0] \nx[1]"
        self.fns=[]
        self.comports=[p[0] for p in lscoms.comports()]
        self.port=0
        self.secected_comport=self.comports[0]
        self.baud=100000
        terminatehooks.append(self.disable)
    def disable(self):
        print "closing Ports"
        self.enabled=False
        self.serial.close()
    def gen(self):
        self.idx+=1
        return (self.idx,np.sin(float(self.idx)/60)+np.random.rand(),np.random.rand())
    def next(self):
        if self.idx<self.maxlen or self.maxlen==0: return self.serial.readline()#self.gen()
        else: raise StopIteration()
    def read(self): return ','.join(map(str,self.gen()[1:]))
    def __iter__(self):return self
    
    def dialog(self,master):
        from PyQt4 import QtCore, QtGui
        
        grid=QtGui.QGridLayout()
        frame=QtGui.QFrame(master)
        frame.setLayout(grid)
        
        self.baudwg=QtGui.QLineEdit(str(self.baud))
        grid.addWidget(QtGui.QLabel("Baudrate"),0,0)
        grid.addWidget(self.baudwg,0,1)
        
        opts=self.comports[:5]
        self.cbox=cbox=QtGui.QComboBox()
        cbox.addItems(opts)
        self.cbox.setCurrentIndex(self.port)
        grid.addWidget(QtGui.QLabel("ComPort"),1,0)        
        grid.addWidget(cbox,1,1)
        
        self.fnswdg=QtGui.QTextEdit()
        self.fnswdg.setPlainText(self.fnstr)
        grid.addWidget(self.fnswdg,2,0,6,2)
        #frame.setMinimumHeight(300)
        return frame
    def ok(self,event):
        print  self.master.focus_get()
        if not self.master.focus_get()==self.fns:
            tkSimpleDialog.Dialog.ok(self.master, event)
    def dialog_ok(self):
        self.baud=int(self.baudwg.text())
        self.port=self.cbox.currentIndex()
        print self.port, self.baud
        self.serial.port=self.comports[self.port]
        self.serial.baudrate=self.baud
        self.fnstr=str(self.fnswdg.toPlainText())
        self.fns=self.parsefns(str(self.fnswdg.toPlainText()))
        self._enable()
        t=Thread(target=self.run).start()
        pass
    def run(self):
        from devices import plot as gui 
        
        gui.initplot()
        self.serial.rtscts=True
        self.serial.dsrdtr=True
        p=SerialWorker(self.serial.port,self.serial.baudrate,self.fnstr)
        p.start()
        #self.serial.open()
        
        #for i in self.next().split(','): gui.pltAddLine(0)
        for i in p.queue.get(): gui.pltAddLine(0)
        gui.selectedlines.update(gui.lines)
        datalen=len(gui.lines)
        print "expecting %d vlues per line"%datalen
        pbuff=deque(maxlen=50)
        self.ts=time.time()
        self.samples=0
        #self.serial.__ini
        
        #self.serial.flushInput()
        while self.enabled:
            self.samples+=1
            if time.time()-self.ts>1 and self.samples>100:
                srate=self.samples/(time.time()-self.ts)
                self.samples=0
                #print self.q.qsize()
                self.ts=time.time()
                gui.samplerate=srate
                gui.master.statusmsgs['srate']="%d/s"%srate
            #str=self.next()
            try:
                #i=map(float,str.split(','))
                data=p.queue.get()
                i=data['values']
                #print i
                s=data['raw']+' '+','.join(["%+05.2f"%j for j in i])
                gui.addtxt(s)
                if self.record: self.record.write(s)
                if len(i)>datalen:
                    for j in i[datalen:]:
                        gui.pltAddLine(0)
                        gui.selectedlines.update(gui.lines)
                        datalen=len(gui.lines)
                    datalen=len(gui.lines)
                    for l in gui.lines[datalen:]:l.buffer.idx=gui.lines[0].buffer.idx
                  
                for j in xrange(datalen):
                    val=0
                    try:val=i[j]
                    except IndexError:i.append(0)
                    
                gui.pltAppendPoints(i)

            except (IndexError,ValueError), e: print "dataerr", str,e
        p.stop()
        p.join()
        print 'p-term'
        #self.serial.close()
        
    @classmethod    
    def parsefns(self,txt):
        lines=txt.split('\n')
        fns=[]
        for l in lines:
            l=l.strip()
            if l and l[0]=="#": continue
            elif l:
                try:fns.append(parsefn(l))
                except: print "Error in Fn", l
        return fns
devices.append(Serial())

def parsefns(txt):
    lines=txt.split('\n')
    fns=[]
    for l in lines:
        l=l.strip()
        if l and l[0]=="#": continue
        elif l:
            try:fns.append(parsefn(l))
            except: print "Error in Fn", l
    return fns
from multiprocessing import Process, Value,Queue,Event
import io
class SerialWorker(Process):
    def __init__(self,port,baud,fnstr=None):
        self.fnstr= fnstr
        self.fns=[]
        
        self.enabled=Value('i')
        self.enabled.value=1
        self.queue=Queue()
        self.port=port
        self.baud=baud
        
        Process.__init__(self)
        
    def run(self):
        self.fns=parsefns(self.fnstr)
        self.serial=serial.Serial()
        self.serial.port=self.port
        self.serial.baudrate=self.baud
        #sio = io.TextIOWrapper(io.BufferedReader(self.serial))
        self.serial.open()
        self.mode=''
        print "starting serial reading"
        while self.enabled.value:
            s0=self.serial.readline().replace('\r','')
            #s0=sio.readline()
            if s0[0]=='b':
                self.mode=s0
                s0=s0[1:]
                
            try:#print s0
                s=s0.split(',')
                try: 
                    vals=[]#map(float,s)
                    for v in s:
                        try : vals.append(float(v))
                        except: pass
    #                 if len(self.fns)<len(vals):
    #                     for i in range(len(self.fns),len(vals)):
    #                         self.fns.append(lambda x: x[i])
                    
                    newvals=[]
                    i=0
                    for fn in self.fns:
                        try: vals.append(fn(vals))
                        except IndexError: pass
                        i+=1
    
                except ValueError:vals=[]
                
                data={'values':vals,'raw':repr(self.mode+'-'+s0)}
                
                self.queue.put(data)
            except: pass
        self.serial.close()
        
    def stop(self):
        self.enabled.value=0
