'''
Created on 25.10.2016

@author: simon
'''
from pydispatch.errors import DispatcherKeyError

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
from gui.plot import Plot 

def minmax(val,a,b):
    assert a<=b
    if val<a:val=a
    if val>b: val=b
    return val
def parsefn(s):
    #from numpy import *
    func=None
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
    name="BufferedSerial"
    description="""
    Receive Buffered Data from uC-Controller. The uC collects Data in two channels until\
    the buffers (each 364Bytes) are filled, followed by transmission via UART to PC. A Hardware\
    Trigger may controlled by the Trigger Dialog. The Timeresolution is adjustable by\
    zooming the x-Axis of the Plot screen, thus the 364 datapoints span the desired time\
    intervall which may be between 10ms and 200ms.
    Note that for times less than 10ms or samplerates above 100k the accuracy of the\
    measurement drops signifciantally. 
    Source for the uC can be found at. http://... 
    The source is written for Atmel's ATMEGA 88pa    
    """
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
        #terminatehooks.append(self.disable)
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
    def handleTriggerChanged(self,signal,sender,arg=None):
        #print self,signal,sender,args,kwargs
        trigger=arg
        print arg
        self.worker.cmdq.put(trigger)
#         self.worker.cmdq.put({'triggerChanged':{
#                                                 'edge':trigger.edge,
#                                                 'value':trigger.value
#                                                 
#                                                 }})
#         pass

    def setTime(self,time):
        """
        set timing window of uC
        :param time: time in ms
        """
        for i in reversed(range(1,8)):
            #find best ADC frequency divisor
            us=1.82476 *(-2.99029 - 0.5915* 2.**i + 1.* time)
            if us>=0:break
        us=minmax(us, 0, 255)
        self.worker.cmdq.put((SET_DIV,i))
        self.worker.cmdq.put((SET_TIME,int(us)))
        
    
    def zoomX(self,dir):
        """
        zoom the timing window in direction dir
        :param dir: int in [+1,-1]
        """
        self.dtime+=max(1,self.dtime*0.1)*dir
        self.dtime=minmax(self.dtime, 4, 255)
        self.setTime(self.dtime)
        for l in self.plot.lines:
            l.buffer.xdata=np.ma.array(np.linspace(0, self.dtime, l.buffer.maxlen))
        self.plot.setXRange(0,self.dtime)
        print self,dir,self.dtime
    def rms(self,main):
        rms=[np.sqrt(np.mean(l.buffer.data**2)) for l in self.plot.selectedlines]

        self.plot.master.statusmsgs['rms']="rms: "+' '.join(["%.2f"%v for v in rms])
    def run(self):
        from devices import plot as gui 
        from pydispatch import dispatcher
        dispatcher.connect(self.handleTriggerChanged, 'triggerChanged')
        self.dtime=50
        gui.current_bufflen=364
        gui.initplot(ylim=(0,255))
        plot=gui
        p=SerialWorker(self.serial.port,self.serial.baudrate,self.fnstr)
        self.worker=p
        p.start()
        #self.serial.open()
        
        
        from globals import framecallbacks

        #for i in self.next().split(','): gui.pltAddLine(0)
        #for i in p.queue.get(): gui.pltAddLine(0)
        #print "data:",p.queue.get()
        gui.pltAddLine(0)
        #gui.selectedlines.update(gui.lines)
        plot=gui
        self.plot=plot
        plot.plt.setDownsampling(False)
        #assert isinstance(plot,Plot)
        #add rms callback

        
        #override zoomx method of plot
        self.dtime=0
        tmpOnZoom=plot.pltZoomX
        plot.pltZoomX=self.zoomX
        #override trigger
        tmptrigger=plot.trigger.trigger
        plot.trigger.trigger=lambda x:1
        #send initial settings to device. functions manipulate gui, thus Do it in mainthread
        #by sending commands to guis eventqueue
        plot.master.eventQueue.put(self.zoomX,[0] )
        plot.master.eventQueue.put(plot.pltAfterTransform)
        p.cmdq.put(plot.trigger)
        
        datalen=len(gui.lines)
        print "expecting %d vlues per line"%datalen
        self.ts=time.time()
        self.samples=0
        #self.serial.__ini
        
        #self.serial.flushInput()
        while self.enabled:

            data=None

            t0=time.time()
            if t0-self.ts>1 and self.samples>1:
                srate=self.samples/(t0-self.ts)
                self.samples=0
                #print self.q.qsize()
                self.ts=t0
                #gui.samplerate=srate
                gui.master.statusmsgs['srate']="%d/s"%srate
           
            #str=self.next()
            try:
                #i=map(float,str.split(','))
                t=time.time()
                datas=p.queue.get()
                
                for data in datas:   
                    #print data  
                    
                    if 'values' in data:
                        
                        self.samples+=1
                        i=data['values']
                        #print i
                        s=data['raw']#+' '+','.join(["%+05.2f"%j for j in i])
                        gui.addtxt(s)
                        if not data['trigger']:
                            for l in plot.lines:l.buffer.idx=0
                            continue
                        if self.record: self.record.write(s)
                        if len(i)>datalen:
                            for j in i[datalen:]:
                                gui.pltAddLine(0)
                                gui.selectedlines.update(gui.lines)
                                datalen=len(gui.lines)
                            plot.master.eventQueue.put(self.zoomX,[0] )    
                            datalen=len(gui.lines)
                            for l in gui.lines:l.buffer.idx=0
                          
    #                     for j in xrange(datalen):
    #                         val=0
    #                         try:val=i[j]
    #                         except IndexError:i.append(0)
                            
                        gui.pltAppendPoints(i)
                       
                    elif 'mode' in data:
                        mode=data['mode']
                        bufflen=data.get('bufflen',364)
                        dt=data.get('t')
                        #if plot.lines[0].buffer.maxlen!=bufflen: plot.setbuffer(bufflen)
                        gui.master.statusmsgs['samplrate']="srate: %d"%(bufflen*1e6/dt)
                        gui.samplerate=(bufflen*1e6/dt)
                #print "tt:",time.time()-t
            except (IndexError,ValueError), e: print "dataerr", str,e
            
        p.stop()
        p.join()
        try: dispatcher.disconnect(self.handleTriggerChanged)
        except DispatcherKeyError: pass
        #restore overriden functions
        plot.pltZoomX=tmpOnZoom
        plot.trigger.trigger=tmptrigger
        #del framecallbacks['buffserial']
        print 'p-term'
        
        
        
    def get_settings(self):
        return {
            "fnstr":self.fnstr,
            'baud':self.baud,
            "port":self.port
            }
        
    def set_settings(self, data):
        try:
            self.fnstr=data["fnstr"]
            self.baud=data["baud"]
            self.port=data["port"]
        except: pass
    
    
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

#************
# Command definitions
#************
SET_TIME=0x01
SET_TRIGGER=0x02
SET_EDGE_RISING=0x03
SET_EDGE_FALLING=0x04
SET_CHANNEL=0x06
CLEAR_TRIGGER=0x05
INC_TIME=0x07
SET_DIV=0x10

EDGE_FALLING=1
EDGE_RISING=2

""" Dataformat"""
class SerialWorkerData():
    trigger=0
    time=1
    vals=2

from gui.plot import Trigger
class SerialWorker(Process):
    
    
    def __init__(self,port,baud,fnstr=None):
        self.fnstr= fnstr
        self.fns=[]
        
        self.enabled=Value('i')
        self.enabled.value=1
        self.queue=PipedQueue()
        self.cmdq=Queue()
        self.port=port
        self.baud=baud
        self.devstate={}
        self.cmd_communicating=Event()
        
        Process.__init__(self)
        
    def run(self):
        self.fns=parsefns(self.fnstr)
        self.serial=serial.Serial()
        self.serial.port=self.port
        self.serial.baudrate=self.baud
        #sio = io.TextIOWrapper(io.BufferedReader(self.serial))
        self.serial.timeout=1
        self.serial.open()
        
        self.mode=''
        print "starting serial reading"
        buffer=deque()
        t=time.time()
        
        while self.enabled.value:
            vals=np.zeros(len(self.fns)+2,'f' )
            if not self.cmdq.empty(): self.send_cmd()
            s0=self.serial.readline().replace('\r','')
            trigger=0

                
            try:
                
                if s0[0]=='b':
                    self.mode=s0
                    vals=s0.split(',')
                    self.mode={'mode':'b','t':int(vals[1]) or 1,'time':vals[3],'trigger_value':vals[2]}
                    s0=s0[1:]
                    self.queue.put([self.mode])
                    continue
                
                
                s=s0.split(',')
                try: 
                    for i in xrange(2):
                        try : vals[i]=float(s[i])
                        except Exception,e: print e
                    if len(s)>=3:trigger=float(s[2])
                    
 
                    i=2
                    for fn in self.fns:
                        try: vals[i]=(fn(vals))
                        except IndexError: pass
                        i+=1
    
                except ValueError:vals=[]
                
                data={'trigger':trigger,'values':vals,'raw':s0[:-1]}
                buffer.append(data)
                
                if time.time()-t>1./25:
                    t=time.time()
                    #print "sending"
                    self.queue.put(list(buffer))
                    buffer.clear()
                
            except Exception,e: print "error in stream",e
        self.serial.close()
        
    def stop(self):
        self.enabled.value=0
    def send_cmd(self):
        self.cmd_communicating.set()
        cmd=self.cmdq.get()
        self.serial.flushInput()
        if isinstance(cmd, Trigger):
            trigger=cmd
            

            
            if self.devstate.get('value')!=trigger.value:
                self.send(SET_TRIGGER, minmax(int(trigger.value),0,255))
            
            ch=3 if trigger.linenumber==0 else 5
            if self.devstate.get('linenumber')!=trigger.linenumber:
                self.send(SET_CHANNEL,ch)
                if trigger.linenumber!=-1:
                    if trigger.edge==1:self.send(SET_EDGE_RISING)
                    else :self.send(SET_EDGE_FALLING)
                else: self.send(CLEAR_TRIGGER)
            elif self.devstate.get('edge')!=trigger.edge:
                if trigger.linenumber==-1: self.send(CLEAR_TRIGGER)
                elif trigger.edge==1:self.send(SET_EDGE_RISING)
                else :self.send(SET_EDGE_FALLING)
            #store new values
            
            self.devstate['linenumber']=trigger.linenumber
            self.devstate['edge']=trigger.edge
            self.devstate['value']=trigger.value
        
       
        elif isinstance(cmd, tuple):
            c,v=cmd
            if self.devstate.get(c)!=v:
                self.send(*cmd)
            self.devstate[c]=v
            
            
        self.cmd_communicating.clear()
        pass
        pass
    def wait_response(self,check=None):
        r=' '
        i=0
        try:
            while i<100 :  #wait for response..
                i+=1
                r=self.serial.readline().replace('\r','')
                if check is None and r[0]=='m': break
                elif check is not None and r[0]=='m' and check==int(r.split('=')[1]):
                    break
                    
                #print s
                #print "xxxxxxxxxxxx cmd response: "+r
        except:i=100
        if i==100: 
            print "cmd error - No or wrong response\n"
            return 0
        
        else:print "cmd resp: "+str(r)+"\n"
        return 1
    def send(self,cmd,val=None):
        """try to send c. max 10repititions"""
        
        c=bytearray([cmd,val or 0])
        print "send cmd: ",c,val
        self.serial.write(c)
        i=0
        while not self.wait_response(val) and i<5:
            #time.sleep(0.5)
            self.serial.flushOutput()
            self.serial.flushInput()
            self.serial.write(c)
            i+=1
            print "send cmd repeat #%d"%i


from multiprocessing import Value,Array,Event,RLock,Lock,Condition
from multiprocessing.sharedctypes import RawArray as SArr
from Queue import Empty
class SharedQueue(object):
    def __init__(self,buffsize=10000,lock=True):
        self.buffer=SArr('f', buffsize)
        self.pos1=Value('i',0,lock=False)
        self.pos2=Value('i',0,lock=False)
        self.buffsize=buffsize
        self.lock=False
        if lock: 
            self.lock=RLock()
            self.cond=Condition(self.lock)
    def put(self,val,lock=False):
        if self.lock:self.lock.acquire()
        self.buffer[self.pos1.value]=val
        self.pos1.value=(self.pos1.value+1)%self.buffsize
        #with self.cond._lock:
        #self.cond.notify_all()
        if self.lock: self.lock.release()
        
    def get(self,block=True,timeout=None,lock=False):
        
        t=time.time()
        timedout=False
        
        if block: 
            self.wait(timeout)     
        if lock:self.lock.acquire()
        ret= self.buffer[self.pos2.value]
        self.pos2.value=(self.pos2.value+1)%self.buffsize
        if lock: self.lock.release()
        return ret
    def getall(self,block=True,timeout=None):
        
        ret=[]
        if not block and self.empty(): return []
        else: self.wait(timeout)
        #self.lock.acquire()
        buf=np.frombuffer(self.buffer,'f')
        if self.pos1.value>self.pos2.value:
            ret=buf[self.pos2.value:self.pos1.value]
        else:
            ret=np.append(buf[self.pos2.value:],buf[:self.pos1.value])
        self.pos2.value=self.pos1.value
        #self.lock.release()
        return ret
    
    def putarr(self,arr):
        self.lock.acquire()
        buf=np.frombuffer(self.buffer,'f')
        start=self.pos1.value
        lmax=self.buffsize-start
        l=len(arr)
        arr=np.array(arr,'f')
        #print len(buf),l
        if l<lmax:buf[start:start+l]=arr[:l]
        else: 
            buf[start:]=arr[:lmax]
            buf[:l-lmax]=arr[lmax:]
        self.pos1.value=(start+l)%self.buffsize
        #self.cond.notify_all()
        self.lock.release()
    
    def wait(self, timeout=None):
        t=time.time()
        timedout=0
#         with self.cond._lock:
#             if self.empty(): self.cond.wait(timeout)
#             if self.empty():raise Empty
#         return
        while self.empty() and not timedout :
            time.sleep(0.05)   
            if timeout and time.time()-t>timeout: raise Empty      
        
        
    def empty(self):
        #self.lock.acquire()
        ret=self.pos1.value==self.pos2.value
        #self.lock.release()
        return ret

from multiprocessing import Pipe
class PipedQueue(object):
    """
        Wrapperclass for pipe to work like a queue
    """
    def __init__(self):
        self.qin,self.qout=Pipe(duplex=False)
    def put(self,val):
        self.qout.send(val)
    
    def get(self):
        #print "pritn empty", self.empty()
        return self.qin.recv()
    def qsize(self):
        return 0
    def empty(self):
        return self.qin.poll()

from collections import deque
class BufferedPipedQueue(object):
    def __init__(self):
        self.qin,self.qout=Pipe(duplex=False)
        self.buffer=deque()
        self.ev=Event()
    def put(self,val):
        self.buffer.append(val)
        if self.ev.is_set():
            #print "sending"
            self.qout.send(list(self.buffer))
            self.buffer.clear()
            self.ev.clear()
    
    def get(self):
        #print "pritn empty", self.empty()
        #self.ev.set()
        #print "reciving"
        return self.qin.recv()
    def qsize(self):
        return 0
    def empty(self):
        return self.qin.poll()

maxnum=600000
def do(q):
    val=0
    count=0
    time.sleep(2)
    t=time.time()
    while count<maxnum:
        val=q.get() 
        count+=1
        #print "got:%f"%val 
    print "count",count,"in",time.time()-t

def do2(q):
    
    #time.sleep(1)
    count=0
    tt=time.time()
    while 1:
        try:
            #time.sleep(0.05)
            t=time.time()
            a=q.getall(timeout=1)
            count+=len(a)
            #if not len(a):raise Empty
            print "count",count,"in",time.time()-t,type(a)
        except Empty: 
            print "finished %d in"%count ,time.time()-tt-1
            break
if __name__=='__main__':
    from multiprocessing import Queue as MPQ
    
    
    q=SharedQueue(buffsize=10000000)
    p=Process(target=do2,args=(q,))
    p.daemon=True
    p.start()
    t=time.time()
    for j in range(2):
        #for i in xrange(maxnum): q.put(i)
        q.putarr(xrange(maxnum))
        time.sleep(0.05)
    print "time putung",time.time()-t
        
    p.join()    
    print '---------------------------------------'
    for q in [SharedQueue(buffsize=1000000,lock=False),
              MPQ(),
              PipedQueue()]:
        print "Testing", q
        p=Process(target=do,args=(q,))
        p.daemon=True
        p.start()
        t=time.time()
        for i in xrange(maxnum+1): q.put(i)
        
        print "time putung",time.time()-t
        p.join()
        print "time join",time.time()-t
        print "----------------------------"