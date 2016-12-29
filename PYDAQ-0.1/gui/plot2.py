'''
Created on 12.11.2016

@author: simon
'''

import pyqtgraph as pg
from plot import Trigger
from collections import deque
from buffers import RingBuffer,downsample
import pyqtgraph.widgets.RemoteGraphicsView
import numpy as np
import time
from PyQt4.QtCore import QPoint,QString,pyqtSignal,Qt, QObject
from StringIO import StringIO
from PyQt4.QtGui import QTransform

plot=None
class PlotWidget(pg.PlotWidget):
    sigMouseDrag=pyqtSignal(object,object)
    sigMouseHover=pyqtSignal(object)
    def __init__(self, parent=None, background='default', **kargs):
        pg.PlotWidget.__init__(self, parent=parent, background=background, **kargs)
        self.onwheel=[]
        self._logmode=(0,0)
    def wheelEvent(self, ev):
        #print dir(ev)
        plt=self.getPlotItem()
        #print ev.pos(),ev.delta(),self.height()
        for fn in self.onwheel: fn(ev.pos(),ev.delta(),self)
        return pg.PlotWidget.wheelEvent(self, ev)
    def mouseMoveEvent(self, ev):
        
        ev.dataPos=self.plotItem.vb.mapSceneToView(ev.pos())
        self.sigMouseHover.emit(ev)
        if ev.buttons() in [Qt.LeftButton,Qt.MidButton,Qt.RightButton]:
            #print ev.buttons()
            self.sigMouseDrag.emit(self,ev)

        return pg.PlotWidget.mouseMoveEvent(self, ev)
    
    def setYRange(self, r, padding=0.05):
        pg.PlotWidget.setYRange(self, r, padding=padding)
        
    def setXRange(self, r, padding=0.05):
        print "setXrange to ",r
        pg.PlotWidget.setXRange(self, r, padding=padding)
    def setLogMode(self,b1,b2):
        pg.PlotWidget.setLogMode(self,b1,b2)
        self._logmode=b1,b2
        print "set logmode to",self._logmode
    
class Plot(QObject):
    sigAutoRangeEnabled=pyqtSignal(bool)
    sigBufferChanged=pyqtSignal(int)
    sigLineAdded=pyqtSignal(object,object)
    sigReset=pyqtSignal()
    sigStart=pyqtSignal()
    def __init__(self,master):
        QObject.__init__(self)
        import qtgui
        #assert isinstance(master, qtgui.Ui_MainWindow)
        self.samplerate=1.
        self.master=master
        self.fouriermode=False
        self.fft_xdata=None
        self.is_rolling=False
        self._logMode=(0,0)
        self.paused=0
        #view=pyqtgraph.widgets.RemoteGraphicsView.RemoteGraphicsView()
        #plt=view.pg.PlotItem()
        #plt._setProxyOptions(deferGetattr=True)
        self.plot=PlotWidget(None)
        self.plt=self.plot.getPlotItem()
        self.plt.setMenuEnabled(False)
        
        master.ui.gridLayout.addWidget(self.plot,0,0)
        self.isdrawn=False
        self.textbuffer=deque(maxlen=1000)
        self.sbuffer=''
        self.terminalEnabled=True
        
        self.current_bufflen=50000
        self.lines=[]
        self.selectedlines=set(self.lines)
        self.plt.setLimits(xMin=0,xMax=self.current_bufflen)
        self.plt.setClipToView(True)
        self.plt.setDownsampling(True,mode='peak')
        self.plt.setMouseEnabled(y=True,x=False)
        
        self.plt.showGrid(True,True)
        
        self.mask=[]
        
        self.plot.onwheel.append(self.onZoomX)
        self.trigger=Trigger(self)
        
        self.autozoom=False
        self.xmm=(0,self.current_bufflen)
        self.ymm=(-1,1)
        self.plot.onwheel.append(lambda pos,delta,plot: self.enableAutorange(False))
        self.plot.sigMouseDrag.connect(lambda plot,ev: self.enableAutorange(False))
        
        self.preappend_filters=[]
        self.sigMouseHover=self.plot.sigMouseHover
    def pltAutoZoom(self):  
        #self.plt.enableAutoRange()
        self._autorange()
        self.autozoom=1 if not self.autozoom else 0
        pass
    def enableAutorange(self,indicator=False):
        if indicator: 
            self.autozoom=1
            self.sigAutoRangeEnabled.emit(True)
        else: 
            self.autozoom=0
            self.sigAutoRangeEnabled.emit(False)
        self.ymm=(0,0)
    
    def _autorange(self):
        ymin,ymax=self.ymm
        xmin,xmax=self.xmm
        for l in self.selectedlines:
            ymax=max(ymax,np.nanmax(l.yData)  )
            ymin=min(ymin,np.nanmin(l.yData) )
        
        
        #print self.ymm
        if (ymin,ymax)!=self.ymm:
            self.setYRange(ymin,ymax)
            self.ymm=(ymin,ymax)
    
    
    def addtxt(self,s):
        if self.terminalEnabled:
            #self.sbuffer+=s+'\n'
            #self.textbuffer=1
            self.textbuffer.append(s)
        pass
    
    def poptxt(self):
        s='\n'.join(self.textbuffer)
        self.textbuffer.clear()
        return s
    
    def initplot(self,ylim=None,xlim=None):
        self.sigBufferChanged.emit(self.current_bufflen)
        self.sigStart.emit()
        self.master.eventQueue.put(self._initplot,(ylim,xlim))
    
    def _initplot(self,ylim=None,xlim=None ):
        ylim=ylim or (-1,1)
        self.lines=[]
        self.selectedlines.clear()
        self.plt.clear()

        self.isdrawn=True
        
        xlim=xlim or (0,self.current_bufflen)
        self.setXRange(*xlim,padding=0)
        self.setYRange(*ylim)

        pass
    
    def _updateplot2(self):
        mask=self.mask
        w=self.plt.width()
        t=time.time()
        for l in self.selectedlines:
            #assert isinstance(l, pg.PlotDataItem)
            

            x,y=l.buffer.getrange(0,l.buffer.bufflen)
            #if l.yData is not None and np.all([y,l.yData]):continue
            y=np.copy(y)    #this is neccessary for the connectionmask to be in sync
            for f in l.prefilters: x,y=f(x,y)
            if self.fouriermode: 
                y=self.fft_ydata(y[~np.isnan(y)])
                #print np.isnan(y).any()
                x=self.fft_xdata if self.fft_xdata is not None else np.linspace(0, self.samplerate/2,len(y))
                #x=np.linspace(0, self.samplerate/2,len(y))
                self.fft_xdata=x
                #print "fft:",time.time()-t
            else:
                y=np.copy(y)
            idx=l.buffer.idx
            for f in l.postfilters: x,y=f(x,y)
            l.setData(x,y)
            
            if not self.fouriermode and self.samplerate<self.current_bufflen*2:
                if l.xDisp is not None and len(self.mask)==len(l.xDisp):
                    self.mask.fill(1)
                else:
                    mask=np.ones(len(l.xDisp),'i') 
                
                self.mask=mask
                fac=1.*l.buffer.bufflen/len(mask)
                
                pos=int(1.*(idx)/fac)
                w=self.plt.width()
                pxoff=len(l.xDisp)/w*5
                mask[pos-pxoff:(pos+pxoff)]=0
                l.curve.opts['connect']=mask
            #l.oldidx=idx
        if self.autozoom: self._autorange()

            
    def fft_ydata(self,ydata):
        try: from scipy.fftpack import fft
        except: from numpy.fft import fft
        data=fft(ydata[:],self.fftlen)
        data=data[1:len(data)/2+1]
        return np.abs(data)
    def enableFFT(self,indicator):
        self.fouriermode=indicator
        if indicator:
            rect=self.plt.viewRect()
            self.tdomXRange=(rect.left(),rect.right())
            self.plt.setMouseEnabled(y=True,x=True)
            self.fftlen=bestFFTlength(self.current_bufflen)
            self.plt.setLimits(xMin=0,xMax=self.samplerate/2)
            self.setXRange(0,self.samplerate/2,padding=0)
            
            print "FFT Length from %d to %d"%(self.current_bufflen,self.fftlen)
        else:
            self.plt.setMouseEnabled(y=True,x=False) 
            self.plt.setLimits(xMin=0,xMax=self.current_bufflen)
            self.setXRange(*self.tdomXRange,padding=0)
        self.enableAutorange(True)
        self.fft_xdata=None
        
    def pltAppendPoint(self,line,point):
        if not self.paused: line.buffer.append(point)
    
    def pltAppendPoints(self,points):
        i=0
        if self.trigger.trigger(points):
            
            for p in points:
                self.pltAppendPoint(self.lines[i],p)
                #print i,p, self.lines[i]
                i+=1
    
    def pltAppendMultiplePoints(self,lofp,line,align=None):
        for f in line.preappend_filters: lofp=np.asarray(f(np.asarray(lofp,dtype=np.double)))
        #print lofp
        if not self.paused: line.buffer.appendmulti(self.trigger.triggerArray(lofp,line),align)
        
    def pltAppendMultiplePointsToLines(self,lofps,align=None): ##TODO: implement Trigger 
        for i in xrange(len(lofps)):
            self.pltAppendMultiplePoints(lofps[i],self.lines[i],align)
    
    def pltAddLine(self,id=0):

        while not self.isdrawn: time.sleep(0.05)
        self.master.eventQueue.put(self._pltAddLine,(0,))
        #self._pltAddLine()
        
        while not self.master.eventQueue.empty():time.sleep(0.05)
    def _pltAddLine(self,id=0):
        #return 0
        line=self.plt.plot(np.zeros(self.current_bufflen),pen='rbgcmykw'[len(self.lines)%8])
        
        line.buffer=RingBuffer([0]*self.current_bufflen,maxlen=self.current_bufflen,masked=False)
    #    line.buffer=RingBuffer(bufflen)
        line.buffer.resize(self.current_bufflen)
        line.skip=0
        line.preappend_filters=[]
        line.prefilters=[]
        line.postfilters=[]
        if self.is_rolling: line.buffer.rolling=True
        self.lines.append(line)
        self.sigLineAdded.emit(self,line)
    #    databuffers.append(deque([0]*bufflen,maxlen=bufflen))
        return line
    
    def onZoomX(self,pos,delta,widget):
        assert isinstance(pos, QPoint)
        assert isinstance(widget, PlotWidget)
        blen=self.current_bufflen
        if widget.height()-pos.y()<50:
            if delta>1:delta=1
            if delta<-1:delta=-1
            if not self.fouriermode:
                return self.pltZoomX(delta)

        
    def pltZoomX(self,delta):

        if delta>0:
            blen=1.1*self.current_bufflen
        else:blen=0.9*self.current_bufflen
        blen=int(max(blen,100))
        self.current_bufflen=blen
        for l in self.lines:
            l.buffer.resize(blen)
            
            #l.setData(*l.buffer.getrange(0,blen))
        self.setXRange(0,blen,padding=0)
        self.plt.setLimits(xMax=blen)
        self.sigBufferChanged.emit(blen)
        #invalidate mask
        self.mask=[]
        pass        

    def hideLine(self,line):
        assert isinstance(line, pg.PlotDataItem)
        line.hide()
        
        
    def showLine(self,line):
        line.show()
    
    def prepareSetRange(self,a,b,ax=0):
        assert a<b
        if self._logMode[ax]:
            a=max(a,1)
            a,b=np.log10(a),np.log10(b)
        return a,b
    def setXRange(self,a,b,padding=0):
        a,b=self.prepareSetRange(a, b,0)
        self.plt.setXRange(a,b,padding=padding)
        
    def setYRange(self,a,b,padding=0):
        a,b=self.prepareSetRange(a, b,1)
        print "setYRange",a,b
        self.plt.setYRange(a,b,padding=padding)
    
    def pltAfterTransform(self): pass
    
    def logx(self,x,y):
        x,y=x[1:],y[1:]
        return x,y
    def setLog(self,b1,b2):
            
        if b1 is not None:
            if b1: 
                self.plt.setDownsampling(False)
                self.plt.setClipToView(False)
            else:
                self.plt.setClipToView(True)
                self.plt.setDownsampling(True)
#             for l in self.lines:
#                 if not self.logx in l.postfilters:
#                     if b1: l.postfilters.append(self.logx)
#                 if not b1:l.postfilters.remove(self.logx)
                
        self.plt.setLogMode(b1,b2)
        self._logMode=(b1,b2)
        
    def resetLinesIdx(self):
        for l in self.lines: l.buffer.idx=0
    
    def setBuffersRolling(self,b):
        self.is_rolling=b
        for l in self.lines:
            l.buffer.rolling=b
            if b: l.buffer.idx=0
    

from sympy.ntheory import factorint

FACTOR_LIMIT = 100

def bestFFTlength(n):
    while max(factorint(n)) >= FACTOR_LIMIT:
        n -= 1
    return n