'''
Created on 24.10.2016

@author: simon
'''
import numpy as np
from devices import  *
#from Tkinter import *

import time#,parser

from collections import deque
from threading import Thread, Event
import multiprocessing
import Queue,traceback
#from numpy import set_string_function
#from array import array

s="""
sin(x)+1
"""
#def parsefn(s):return lambda x: eval(parser.expr(s).compile(),dict({'x':float(x)}.items()+vars(np).items() ) )
def parsefn(s):
    #from numpy import *
    func=None
    try:
        
        #print s
        s=(   
"""
#from numpy import *
#print globals()
def func(x):
    return %s
print func(1)
#end            
"""%s
         )
        scope=locals()
        scope.update(vars(np))
        exec(s,scope)
        #print "fn evals to", func(1)
    except: print traceback.print_exc()
    return func

class DataGen(DeviceBase):
    name="Datagenearator"
    def __init__(self,maxlen=0):
        DeviceBase.__init__(self)
        self.maxlen=maxlen
        self.idx=0
        self.fnstr="#enter a Function(x) per line (eg. x**2+1) to recalculate received values \n\r sin(1.*x/60)"
        self.fns=self.parsefns(self.fnstr)
        self.samplerate=2000
        self.enabled=1
    def gen(self):
        self.idx+=1
        return [fn(self.idx) for fn in self.fns]
        #return (self.idx,np.sin(float(self.idx)/60)+np.random.rand(),np.random.rand())
    def next(self):
        if (self.idx<self.maxlen or self.maxlen==0) and self.enabled: return self.read()#self.gen()
        else: raise StopIteration()
    def read(self): 
        s=','.join(map(str,self.gen()))
        
        if self.record: 
            try:self.record.write(s+"\n")
            except ValueError: pass
        return s
    def __iter__(self):return self
    
    
     
    def dialog(self,master):
        from PyQt4 import QtCore, QtGui
        #assert isinstance(master, QtGui.QFrame)
        grid=QtGui.QGridLayout()
        
        #master.setLayout(grid)
        frame=QtGui.QFrame(master)
        frame.setLayout(grid)
        #self.fnwidget=QtGui.QLineEdit(self.fnstr)
        #grid.addWidget(QtGui.QLabel("Function"),0,0)
        #grid.addWidget(self.fnwidget,0,1)
        self.srwidget=QtGui.QLineEdit(str(self.samplerate))
        grid.addWidget(QtGui.QLabel("Samplerate"),1,0)
        grid.addWidget(self.srwidget,1,1)
        
        self.fns=QtGui.QTextEdit()
        self.fns.setPlainText(self.fnstr)
        grid.addWidget(self.fns,2,0,6,2)
        return frame
#         Label(master, text="Function:").grid(row=0)
#         svar=StringVar(value=self.fnstr)
#         self.e1 = Entry(master,textvariable=svar)
#         
#         self.e1.grid(row=0,column=1)
#         
#         Label(master, text="Rate in Hz:").grid(row=1)
#         self.e2 = Entry(master,textvariable=StringVar(value=str(self.samplerate)) )
#         self.e2.grid(row=1,column=1)
    def handleEvent(self,sender,*args,**kwargs):print sender,args,kwargs
    
 
    def run(self):
        from devices import plot as gui
        from globals import framecallbacks
        from multiprocessing import Pool
        from pydispatch import dispatcher
        dispatcher.connect(self.handleEvent,signal= 'triggerChanged',sender=dispatcher.Any)
        self.gui=gui
        pbuff=deque(maxlen=50)
        self.ts=time.time()
        gui.initplot()
        self.idx=0
        self.samples=0

        for i in self.next().split(','): gui.pltAddLine(0)
        #show all line
        targetsr=self.samplerate
        gui.selectedlines.update(gui.lines)
        self.tp=time.time()
        p=DataWorker(str(self.fnstr))
        p.start()
        e=Event()
        global fns
        fns=self.fns
    
        data=None
        def framecb(parent):
            diff=time.time()-self.tp
            num=int(diff*self.samplerate) or 1
            self.tp=time.time()
            if self.enabled: p.request(self.idx, self.idx+num)
            self.idx+=num
       
        framecallbacks['datagen']=framecb
        while self.enabled:
            data=p.get(timeout=.1)
            if data is None: continue
            #print data[:10]
#            if time.time()-tp>=1./self.samplerate:
#                tp=time.time()
#                i=self.next()
#                 self.samples+=1
            if time.time()-self.ts>1 and self.samples>100:
                srate=self.samples/(time.time()-self.ts)
                self.samples=0
                #print self.q.qsize()
                self.ts=time.time()
                self.gui.samplerate=srate
                self.gui.master.statusmsgs['srate']="%d/s"%srate
                self.gui.master.statusmsgs['outqsize']="outqsize: %d"%p.out.qsize()
                self.gui.master.statusmsgs['inqsize']="reqqsize: %d"%p.cmd.qsize()
            #t=time.time()
            lofps=np.array(data).transpose()
            self.gui.pltAppendMultiplePointsToLines(lofps,1)
            for i in data: self.makedata(i)
            #print "ttok :",time.time()-t
            self.samples+=len(data)
        print "disabling worker..."
        p.disable()
        p.join()
        print "disabled!"
    def makedata(self,i):
        #i=self.next()

        str=i
        
#        i=map(float,i.split(','))
        if self.gui.terminalEnabled:
            self.gui.addtxt(s=','.join(["%+05.2f"%j for j in i]))
        
        #time.sleep(1./self.samplerate)
#             target_time = time.clock() + 1./self.samplerate
#             while time.clock() < target_time:
#                 pass
        #self.gui.pltAppendPoints(i)
        #for j in range(len(i)):self.gui.pltAppendPoint(self.gui.lines[j], i[j])
    def dialog_ok(self):
        self.enable()
        txt=str(self.fns.toPlainText())
        self.fns=fns=self.parsefns(str(self.fns.toPlainText()))
        
        self.fnstr=txt
        self.fn=fns[0]
        self.samplerate=int(self.srwidget.text())
        
        print txt, self.samplerate
        t=Thread(target=self.run)
        t.daemon=True
        t.start()
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
        
    def disable(self):
        self.enabled=0
        
    def enable(self):
        self.enabled=1
    
    def get_settings(self):
        return {
                'fnstr':self.fnstr,
                'samplerate':self.samplerate
                }
    
    def set_settings(self, data):
        for k,v in data.iteritems():
            try: setattr(self, k, v)
            except AttributeError: pass
devices.append(DataGen())



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

class DataWorker(multiprocessing.Process):
    def __init__(self,fnstr):
        self.fnstr=fnstr
        
        #self.fns=fns
        multiprocessing.Process.__init__(self)
        self.cmd=PipedQueue()#multiprocessing.Queue()
        self.out=PipedQueue()#multiprocessing.Queue()
        self.do=multiprocessing.Value('i')
        self.do.value=1
        


    def request(self,a,b):self.cmd.put((a,b))
    def run(self):
        self.fns=parsefns(self.fnstr)
        nump=4
        ps=[DataSubWorker(self.fnstr) for i in range(nump)]
        [p.start() for p in ps]
        while self.do.value:
            try:
                data=[]
                a,b=self.cmd.get(timeout=.1)
                r=(b-a)/nump 
                if r>0:
                    
                    for i in range(nump):
                        ps[i].request(a+i*r,a+(i+1)*r)
                    for i in range(nump): data.extend(ps[i].get())
                else: #calc data directly
                    data=[[fn(float(x)) for fn in self.fns] for x in xrange(a,b)]
                self.out.put(np.array(data))
            except Queue.Empty: pass
            #print "worker running",self.do.value
        print "worker left loop"
        [p.disable() for p in ps]
        self.out.cancel_join_thread()
    def get(self,timeout=None): 
        try: return self.out.get(timeout=timeout)
        except: return None
    def disable(self): 
        self.do.value=0
class DataSubWorker(DataWorker):
    def __init__(self, fnstr):
        DataWorker.__init__(self, fnstr)
       
        
    def run(self):
        import random
        np.random.seed(self.ident)
        self.fns=parsefns(self.fnstr)
        while self.do.value:
            try:
                a,b=self.cmd.get(timeout=.1)
                data=[[fn(float(x)) for fn in self.fns] for x in xrange(a,b)]
                self.out.put(data)
            except Queue.Empty: pass
            #print "worker running",self.do.value
        print "worker left loop"
        self.out.cancel_join_thread()        
print "loaded Datagen"
# if __name__ == '__main__':
#     dg=DataGen(100)
#     for i in dg: print i 

from multiprocessing import Pipe
class PipedQueue(object):
    def __init__(self):
        self.qin,self.qout=Pipe(duplex=False)
    def put(self,val):
        self.qout.send(val)
    
    def get(self,timeout=None):
        self.qin.poll(timeout)
        if timeout and not self.qin.poll(): raise Queue.Empty
        return self.qin.recv()
    def qsize(self):
        return 0
    def cancel_join_thread(self):
        #self.qin.close()
        #self.qout.close()
        pass
    
    

ncache=None
samples=50000
tt=0
def pinknoise(i,gain=20.,dx=20.):
    global ncache,tt
    
    if i%samples==0 or ncache is None: 
        tt=time.time()
        ps=np.exp(2*np.pi*np.complex(0,1.)*np.random.rand(samples-1))
        x=np.arange(samples,dtype='complex')
        f=data=gain/(x+dx)
        Np = (len(f) - 1) // 2
        phases = np.random.rand(Np) * 2 * np.pi
        phases = np.cos(phases) + 1j * np.sin(phases)
        f[1:Np+1] *= phases
        f[-1:-1-Np:-1] = np.conj(f[1:Np+1])
        ncache=np.real(np.fft.ifft(f))
        #ncache=np.fft.ifft(data)[:samples]
    return np.real(ncache[i%(samples)])

def _pinknoise(i):
    return np.real(ncache[i%(samples)])
np.pinknoise=pinknoise



if __name__ == '__main__':
    #import pyximport; pyximport.install()
    #import ctools.filters as filters
    from ctools import filters
    x=np.sin(np.arange(50000,dtype=np.float)/10)**2
    t=time.time()
    x1=filters.meanfilter2(x,5000)
    print time.time()-t
    N=5000
    t=time.time()
    x2=np.convolve(x, np.ones((N,))/N, mode='valid')
    print time.time()-t
    
    from matplotlib import pyplot
    from gui.buffers import downsample
    
    #x=downsample(x,2000)
    #x1=downsample(x1,2000)
    pyplot.plot(x[:])
    pyplot.plot(x1)
    #pyplot.plot(x2)
    pyplot.show()
    #_pinknoise(0)