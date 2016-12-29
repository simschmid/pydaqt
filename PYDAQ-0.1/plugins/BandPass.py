'''
Created on 29.11.2016

@author: simon
'''
from plugins import plugins
from PyQt4 import QtGui,QtCore
from ctools.filters import IIR
from scipy.signal.filter_design import iirfilter

class BandPass(object):
    '''
    Plugin for PyDaq which adds some filters (iir and fft)
    '''


    def __init__(self, app):
        
        '''
        Adds a Dialog for applying a Bandpassfilter with cutoff-frequncies f1,f2 to the underlying data.
        @type app: gui.qtgui.UI_Main
        '''
        
        filter=QtGui.QAction("BandFilter",app)
        app.ui.plotcontrols.addAction(filter)
        filter.triggered.connect(lambda: FilterDialog(app).show() if not FilterDialog.instance else FilterDialog.instance.restore())
        pass
        
        
        
        
class FilterDialog(QtGui.QDialog):
    """
    Dialog to apply a Filter to a line drawn by gui.plot2. For each line an instance of 
    BandpassWidget is added
    """
    instance=None
    def __init__(self, app):
        """
        @type app: gui.qtgui.UI_Main
        """
        
        QtGui.QDialog.__init__(self, app)
        FilterDialog.instance=self
        self.setWindowTitle("Filters")
        self.app=app
        self.colsAdjusted=0
        lo=QtGui.QGridLayout()
        #lo.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(lo)
        i=0
        self.resize(500,200)
        lbls="Line,Type,Band,Order,fmin,fmax,FFT,Invert,On".split(',')
        self.header=[]
        for s in lbls:
            lbl=QtGui.QLabel(s)
            lo.addWidget(lbl,0,i)
            self.header.append(lbl)
            i+=1
        i=0
        frame=QtGui.QScrollArea()
        frame.setFrameShape(0)
        qslo=QtGui.QGridLayout()
        qslo.setMargin(0)
        
        qslo.setAlignment(QtCore.Qt.AlignTop)
        frame.setLayout(qslo)
        lo.addWidget(frame,1,0,2,0)
        if not hasattr(app, 'bandpassfilters'):
            app.bandpassfilters={}
        for l in app.plot.lines:
            bpw=app.bandpassfilters.get(l) or BandPassWidget(app,l)
            app.bandpassfilters[l]=bpw
            i+=1
            #lbl=QtGui.QLabel("Line %d"%i)
            row=i-1
            #bpw.f1.setMaximum(app.plot.samplerate/2)
            #bpw.f2.setMaximum(app.plot.samplerate/2)
            
            #qslo.addWidget(lbl,row,0)
            col=0
            for w in bpw.widgets:
                #w.resize(30,10)
                qslo.addWidget(w,row,col)
                col+=1
    
    def paintEvent(self, *args, **kwargs):
        """
        hook into paintevent to resize the second grid layout according to the first one
        """
        QtGui.QDialog.paintEvent(self, *args, **kwargs)
        try:
            if self.colsAdjusted>2:return
            header=self.header[:]
            cols=self.app.bandpassfilters.values()[0].widgets
            for i in range(min(len(header),len(cols))):
                w1=cols[i].width()
                w2=header[i].width()
                if w1>w2: header[i].setMinimumWidth(w1)
                else : cols[i].setMinimumWidth(w2)
            self.colsAdjusted+=1
            self.update()
        except Exception,e: print e
    
    def restore(self):
        """
        restore the window when it was previously closed
        """
        self.show()
        self.activateWindow()
    
    def hideEvent(self, *args, **kwargs):
        """
        Closing the window doesnt destroy it by default. 
        Force destruction Destruction
        """
        self.destroy()
        FilterDialog.instance=None
        return QtGui.QDialog.hideEvent(self, *args, **kwargs)
class BandPassWidget(QtGui.QWidget):
    """
    This class holds all widgets for adjusting the filteroptions. 
    """
    def __init__(self, app,line):
        """
        Create all neccessary widgets
        @type app: gui.qtgui.UI_Main
        """
        QtGui.QWidget.__init__(self,app)
        
        filters=["butter","cheby1","cheby2","ellip","bessel"]
        btypes=["band","low","high"]
        srate=app.plot.samplerate/2
        self.plot=app.plot
        self.line=line
        lbl=QtGui.QLabel("Line %d"%self.plot.lines.index(line))
        self.setWindowTitle("BandPass")
        self.f1=QtGui.QSpinBox()
        self.f2=QtGui.QSpinBox()
        self.f1.setMaximum(99999999)
        self.f2.setMaximum(99999999)
        self.f1.setMinimumWidth(60)
        self.f2.setMinimumWidth(60)
        self.f2.setValue(srate)
        
        self.filterBox=QtGui.QComboBox()
        self.filterBox.addItems(filters)
        
        self.btypesBox=QtGui.QComboBox()
        self.btypesBox.addItems(btypes)
        
        self.useFftCb=QtGui.QCheckBox()
        self.useFftCb.stateChanged.connect(self.restart)
        self.useFft=0
        self.useFftFallBack=0
        
        self.inv=QtGui.QCheckBox()
        self.en=QtGui.QCheckBox()
        
        self.orderW=QtGui.QSpinBox()
        self.orderW.setMinimum(1)
        
        self.widgets=[lbl,self.filterBox,self.btypesBox,self.orderW,self.f1,self.f2,self.useFftCb,self.inv,self.en]
        self.bpf=IIRFilter(line.buffer.data, 0, srate,app.plot.samplerate)
        self.f1.valueChanged.connect(self.changed)
        self.f2.valueChanged.connect(self.changed)
        self.orderW.valueChanged.connect(self.changed)
        self.en.stateChanged.connect(self.toggle)
        self.inv.stateChanged.connect(self.changed)
        
        self.btypesBox.currentIndexChanged.connect(self.changed)
        self.filterBox.currentIndexChanged.connect(self.changed)
        
        app.plot.sigBufferChanged.connect(self.bufchanged)
    
    def bufchanged(self):
        """
        Update the filters frequency scaling on bufferlength-changes
        """
        self.bpf.updateValues(self.line.buffer.data)
    def changed(self,*args,**kwarg):
        """
        Update the filter according to the changed values in gui
        """
        f1=self.f1.value()
        f2=self.f2.value()
        if f2>self.plot.samplerate/2:f2=self.plot.samplerate/2
        
        btype=self.btypesBox.currentText()
        self.f1.setEnabled(True)
        self.f2.setEnabled(True)
        if btype=='low':
            self.f1.setEnabled(False)
            f1=False
        elif btype=='high':
            self.f2.setEnabled(False)
            f2=False
        elif btype=='band':
            if f1>f2:f1=f2
            self.f1.setValue(f1)
            self.f2.setValue(f2)
            
        if self.useFftCb.isChecked(): self.useFft=1
        else: self.useFft=0
        
        #try to use iir filter when in fallbackmode
        if self.useFftFallBack:
            self.useFftFallBack=0
            self.useFft=0
            self.useFftCb.setChecked(False)
        
        try:self.bpf.updateValues(self.line.buffer.data,f1, f2,self.inv.isChecked(),
                              order=self.orderW.value(),ftype=str(self.filterBox.currentText()))
        except ValueError: 
            #Fallback to FFT filter-fode
            if not self.useFft:
                self.useFftCb.setChecked(1)
                self.useFft=1
                self.toggle()
                self.useFftFallBack=1
                return
    def toggle(self):
        """
        Toggle the filter on or off.
        """
        #remove all filter added by this plugin
        try: 
            while 1:self.line.prefilters.remove(self.bpf.getData)
        except: pass
        try: 
            while 1:self.line.preappend_filters.remove(self.bpf.iirArr)
        except: pass
        #add filter as specified by the user
        if self.en.isChecked():
            if self.useFft:
                self.line.prefilters.append(self.bpf.getData)
            else:
                self.line.preappend_filters.append(self.bpf.iirArr)

    def restart(self):
        self.changed()
        if self.en.isChecked(): 
            self.en.setChecked(False)
            self.toggle()
            self.en.setChecked(True)
            self.toggle()
import numpy as np
try:
    from scipy import fftpack as fft
except ImportError:
    from numpy import fft
    
from gui.plot2 import bestFFTlength
import time
class BandPassFilter:
    """
    A Filter based on FFT.
    """
    def __init__(self,a,f1,f2,srate):
        """
        :param a: numpy_array with data to filter
        :param f1, lower cutoff frequency. Filter is low pass if f1=0
        :param f2, upper cutoff frequency. Filter is highpass if f2=0
        :param srate: Samplerate
        """
        self.srate=srate
        self.a=a
        self.ftype='butter'
        self.inverted=False
        self.order=1        
        self.updateValues(a,f1,f2,False)

        
    def getData(self,x,y):
        """
        return the filtered data
        """
        y=y[:self.bestfftl]
        out= x[:self.bestfftl],np.real(fft.ifft(fft.fft(y)*self.af))
        return out
    def getarray(self,arr):
        #if arr.shape[0]!=self.af.shape[0]: pass
        return np.real(fft.ifft(fft.fft(arr)*self.makeAf(arr)))
    def makeAf(self,arr):
        i1=self.i1=self.f1*len(arr)/self.srate+1 
        i2=self.i2=self.f2*len(arr)/self.srate+1 
        self.af=np.zeros(arr.shape[0])
        self.af[i1:i2]=1
        self.af[-i2:-i1]=1
        return self.af
    def updateValues(self,a=None,f1=None,f2=None,inverted=None,order=None,ftype=None):
        """
        Update filter params
        :param a: data array
        :param f1: lower cutoff freq
        :param f2: upper cutoff freq
        :param order: the filters order
        :param ftype (str): the filtertype, one of butter, cheby1 cheby2, ellip or bessel
        :raise exception: ValueError if filter will be unstable 
        """
        if f1 is not None: self.f1=f1 
        if f2 is not None: self.f2=f2
        if a is not None:self.a = a
        if order: self.order=order
        if ftype is not None and ftype in ['butter','cheby1','cheby2','ellip','bessel']:
            self.ftype=ftype
        i1=self.i1=self.f1*len(self.a)/self.srate if self.f1 else False
        i2=self.i2=self.f2*len(self.a)/self.srate if self.f2 else False
        self.bestfftl=bestFFTlength(len(self.a))
        self.a=self.a[:self.bestfftl]
        
        if not inverted:
            self.af=self.makeG(i1, i2)
            #self.af=np.zeros(self.a.shape[0])
            #self.af[i1:i2]=1
            #self.af[-i2:-i1]=1
        else:
            self.af=np.ones(self.a.shape[0])
            self.af[i1:i2]=0
            self.af[-i2:-i1]=0
        
    def _makeG(self,i1,i2):
        x=np.arange(1,self.a.shape[0]+1,dtype="f")*1j
        l=self.a.shape[0]
        n=self.order#*2
        print i1,i2,l
        y=None
        if not i1: y=1/(1+(x/i2)**(2*n))
        elif not i2: y=1/(1+(i1/x)**(2*n))
        else:y=1/(1+(i1/x)**(2*n))*1/(1+(x/i2)**(2*n))
        y=y**0.5
        try: y[l/2::]=y[:l-l/2][::-1]
        except ValueError: pass
        return np.abs(y)
    def makeG(self,i1,i2):
        """
        Generates Gainfunction G(s)=|H(s)|
        """
        print "makingG:",i1,i2
        x=np.arange(1,self.a.shape[0]+1,dtype='f')
        k=1 #gain factor
        n=self.order
        if i1 and i2:
            x=tflpbp(x, i1, i2)
            #n=2*n
        elif i1:
            x=tflphp(x, i1)
        elif i2:
            x=tflplp(x, i2)
        
        y=None
        if self.ftype=='butter': y=gButter(x, n)
        elif self.ftype=='cheby1': y=gCheby1(x, n)
        k=1/np.nanmax(y)
        print i1,i2,k
        l=self.a.shape[0]
        y[l/2::]=y[:l-l/2][::-1]
        return y*k
    
from threading import Lock
class IIRFilter(BandPassFilter):
    def __init__(self, a, f1, f2, srate):
        self.iir=IIR(f1=f1,f2=f2,samplerate=srate)
        self.lock=Lock()
        BandPassFilter.__init__(self, a, f1, f2, srate)
        
    def updateValues(self, a=None, f1=None, f2=None, inverted=None, order=1,ftype='butter'):
        BandPassFilter.updateValues(self, a=a, f1=f1, f2=f2, inverted=inverted, order=order,ftype=ftype)
        btype='bandpass'
        if f1 is not None or f2 is not None:
            if f1: f1=f1/(0.5*self.srate)
            if f2: f2=f2/(0.5*self.srate)
            fs=(f1,f2)
            if not f1 and f2: 
                fs=f2
                btype='lowpass'
            if not f2 and f1: 
                fs=f1
                btype='highpass'
            b,a=iirfilter(order,fs,ftype=ftype,btype=btype,rp=.1,rs=10)
            #print b,a
            stable=np.all(np.abs(np.roots(a))<1)
            if not stable:
                raise ValueError("The filter is not stable")
                #TODO: Fallback to fft mode
            with self.lock:
                self.iir.set_ba(b,a)
           
            #self.iir=IIR(b,a)
    
    def iirArr(self,arr):
        out=[]
        with self.lock:
            out=self.iir.filterArr(arr)
            #print np.asarray(out)
        return out
    pass

def butterpoles(n,k):
    return np.exp(1j*(2*k+n-1)*np.pi/2/n  )
def butter(x,n):
    dn=1
    for k in xrange(n): dn*=x-butterpoles(n, k) 
    return 1/dn

def gButter(x,n):
    return 1/(1+x**(2*n))**0.5
def gCheby1(x,n,epsilon=.1):
    return 1/(1+(epsilon*cheby(x,n))**2)**0.5
def gCheby2(x,n,epsilon=.1):
    return 1/(1+1/(epsilon*cheby(1/x,n))**2)**0.5
def cheby(x,n):
    x1 = lambda x:np.cos(n*np.arccos(x))
    x2=lambda x: np.cosh(n*np.arccosh(x))
    return np.piecewise(x,[x<=1,x>1],[x1,x2])
def tflplp(x,fc): return x/fc
def tflphp(x,fc): return fc/x
def tflpbp(x,f1,f2):
    f0=(f1*f2)**.5
    df=f2-f1
    q= f0/df
    return q*(x/f0+f0/x)
    
plugins.append(BandPass)