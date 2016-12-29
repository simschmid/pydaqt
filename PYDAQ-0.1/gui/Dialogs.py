'''
Created on 29.10.2016

@author: simon
'''
from ui import start
from PyQt4 import QtCore, QtGui,uic
from ui.start import Ui_StartDialog as StartDialog
from ui.selectlines import Ui_SelectLines
from ui.triggerdialog import Ui_TriggerDialog
import devices
from PyQt4.Qt import QString
from plot import Plot
from pydispatch import dispatcher
import ctools
#from qtgui import UI_Main

class StartDialog(StartDialog,QtGui.QDialog):
    """
    Dialog for choosing and starting one of the available devices
    :param parent: The paretn gui element
    :param selected_device: the previously selected device
    """
    def __init__(self,parent,selected_device=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)
        self.devices_cbox.addItem('Please Select')
        for dev in devices.devices: self.devices_cbox.addItem(dev.name)
        self.devices_cbox.currentIndexChanged.connect(self.select_dev)
        self.dev_widgets={0:self.textBrowser}
        #self.selected_device=selected_device

        
        
        self.parent=parent
        self.buttonBox.accepted.connect(self.ok)
        self.setWindowModality(QtCore.Qt.WindowModal)
        if selected_device:
            selected_device_index=devices.devices.index(selected_device)+1
            self.select_dev(selected_device_index)
            self.devices_cbox.setCurrentIndex(selected_device_index)
    def select_dev(self,ev):
        """
        Callback for QComboBox 
        """
        print ev
        for k in self.dev_widgets.values():k.hide()
        f=self.dev_widgets.get(ev,None)
        
        self.dev_frame_layout.setAlignment(QtCore.Qt.AlignTop)
        if f: f.show()
        else:
            f=(devices.devices[ev-1].dialog(self))
            self.dev_widgets[ev]=f
            self.dev_frame_layout.addWidget(f)
        self.selected_device=None
        if ev>0:
            print "naming"
            dev=devices.devices[ev-1]
            self.selected_dev_name.setText(devices.devices[ev-1].name)
            if hasattr(dev,'description') :self.selected_dev_name.setToolTip(dev.description)
            self.selected_device=devices.devices[ev-1]
        else: self.selected_dev_name.setText("no device selected")
        self.selected_dev_name.repaint()
        #self.parent.process_events()
    def ok(self):
        """
        self explanatory
        """
        self.selected_device.dialog_ok()
        self.parent.active_device=self.selected_device
        self.parent.last_selected_device=self.selected_device
    def reject(self, *args, **kwargs):
        """
        :see :StartDialog.ok
        """
        self.parent.playaction.setChecked(False)
        return QtGui.QDialog.reject(self, *args, **kwargs)
        
    
class SelectLines(Ui_SelectLines,QtGui.QDialog):
        """
        Dialog for selecting lines
        """
        def __init__(self,parent):
            gui=parent
            self.plot=plot=gui.plot
            QtGui.QDialog.__init__(self,parent)
            self.setupUi(self)
            assert isinstance(self.lineslist, QtGui.QListWidget)
            itms=[]
            for i in range(len(gui.plot.lines)): 
                itm=QtGui.QListWidgetItem('Line %d'%(i+1))
                itms.append(itm)
                self.lineslist.addItem(itm)
                if plot.lines[i] in plot.selectedlines:self.lineslist.setItemSelected(itms[i],True)
            #self.lineslist.addItems(itms)
            #if hasattr(parent, 'selectlines_visible'): self.deleteLater()
            self.setWindowModality(QtCore.Qt.WindowModal)
            self.buttonBox.accepted.connect(self.ok)
            #self.show()
        def ok(self):
            selitms=self.lineslist.selectedItems()
            #self.plot.ax.lines=[]
            for l in self.plot.selectedlines: self.plot.hideLine(l)
            self.plot.selectedlines.clear()
            for i in selitms:
                idx=self.lineslist.row(i)
                print idx
                self.plot.selectedlines.add(self.plot.lines[idx])
                #self.plot.ax.lines.append(self.plot.lines[idx])
                self.plot.showLine(self.plot.lines[idx])
                
class TriggerDialog(Ui_TriggerDialog,QtGui.QDialog):    
    """
    Dialog for controlling the DataTrigger
    @see: gui.plot.Trigger
    """
    dnum=0 
    dialog=None
    def dec_num(self): TriggerDialog.dnum-=1
    def __init__(self, parent):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)
        
        if self.dnum>0:
            TriggerDialog.dialog.activateWindow()
            raise ValueError("dd")
        
        TriggerDialog.dialog=self
        TriggerDialog.dnum+=1
        self.lineselector.addItem('None')
        plot=parent.plot
        #assert isinstance(plot, Plot)
        self.plot=plot
        i=0
        for l in plot.lines:
            self.lineselector.addItem("line %d"%(i+1))
            if l==plot.trigger.line: self.lineselector.setCurrentIndex(i+1)
            i+=1
        self.lineselector.currentIndexChanged.connect(self.linechanged)
        self.ok.clicked.connect(lambda:self.close())
        #self.radioFalling.toggled.connect(self.radiotog)
        self.radioRising.toggled.connect(self.radiotog)
        
        self.triggervalue.setMaximum(5555555)
        self.triggervalue.setValue(plot.trigger.value)
        
        self.triggervalue.valueChanged.connect(self.triggervaluechanged)
        self.treshold.setValue(plot.trigger.sense)
        self.treshold.valueChanged.connect(self.thresholdChanged)
    def closeEvent(self, *args, **kwargs):
        self.dec_num()
        return QtGui.QDialog.closeEvent(self, *args, **kwargs)
    def linechanged(self,n):
        print n
        line=None
        if n: line=self.plot.lines[n-1]
        self.plot.trigger.setline(line)
        self.sendEvent()
    def radiotog(self,bool):
        if self.radioFalling.isChecked():self.plot.trigger.edge=-1
        else : self.plot.trigger.edge=1
        self.sendEvent()
    def triggervaluechanged(self, val):
        self.plot.trigger.value=val
        self.sendEvent()
    def thresholdChanged(self,val):
        if val>0: self.plot.trigger.setTreshold(val)
        else: self.treshold.setValue(self.plot.trigger.sense)
        self.sendEvent() 
    def sendEvent(self):
        print "send ev"
        dispatcher.send(signal='triggerChanged',sender=dispatcher.Any,arg=self.plot.trigger)
import matplotlib,numpy as np
class Fourierplot():
    def __init__(self, parent, **kwargs):
        self.parent=parent
        import matplotlib.pyplot as plt
        buffer=parent.plot.lines[0].buffer

        
        pdata=[]
        for l in parent.plot.selectedlines:
            data=np.abs(np.fft.fft(l.buffer.data))
            data=data[:len(data)/2]
            pdata.append(data)
        print  parent.plot.samplerate/2,len(pdata[0])
        x=np.linspace(0, parent.plot.samplerate/2,len(pdata[0]))
        self.plt=plt
        
        for d in pdata: plt.semilogx(x,d)
        plt.ylabel('some numbers')
        
    pass
    def show(self):
        self.plt.show()
 
from globals import framecallbacks     
from ctools import filters

class LiveDataDock(QtGui.QDockWidget):
    """
    Dockwidget for displaying data values, rms, mean
    """
    id=1
    livewidgets=[]
    lastwidget=None
    def __init__(self,parent):
        #assert isinstance(parent, UI_Main)
        QtGui.QDockWidget.__init__(self,parent)
        uic.loadUi('gui/ui/livedata.ui', self)
        #self.setFloating(True)
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea|QtCore.Qt.LeftDockWidgetArea)
        """hide lineselector dropbox. This is implemented as context menu"""
        self.lines.hide()
        #self.count.hide()
        #self.countlabel.hide()
        assert isinstance(self.count, QtGui.QSlider)
        self.count=self.count
        assert isinstance(self.countEdit, QtGui.QSpinBox)
        self.countEdit=self.countEdit
        
        """Set behaviour of kernelsize adjustment widgets"""
        self.count.setEnabled(False)
        self.count.setValue(1)
        self.countEdit.setEnabled(False)
        self.cb_meanfilter.clicked.connect(self.toggleMeanFilter)
        self.cb_rmsfilter.clicked.connect(self.toggleRMSFilter)
        self.count.valueChanged.connect(self.handleCountChange)
        self.countEdit.valueChanged.connect(self.handleCountEditChange)
        self.countValue=1
        self.meanfilter_enabled=False
        self.rmsfilter_enabled=False
        
        self.setWindowTitle("Livedata %d"%LiveDataDock.id)
        self.idx=LiveDataDock.id-1
        LiveDataDock.id+=1

        LiveDataDock.livewidgets.append(self)
        LiveDataDock.lastwidget=self
        
        self.plot=parent.plot
        self.plot.sigBufferChanged.connect(self.handleBufferChange)
        self.plot.sigStart.connect(self.reset)
        
        
        framecallbacks['live%d'%(LiveDataDock.id-1)]=self.insertValues
        
        self.fcnt=0
        self.frameskip=5
        
        #self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.enabled=enabled=QtGui.QAction('Enable',self,checkable=True)
        enabled.setChecked(True)
        self.linegroup=QtGui.QActionGroup(self)
        
        self.selectedFilter=filters.meanfilter2
        
        self.ycache=None
        self.oldy=None
        self.lastm=0
        self.lastidx=0
        
        #set initial values
        self.handleBufferChange(self.plot.current_bufflen)
        
    def reset(self):
        self.cb_meanfilter.setChecked(False)
        self.cb_meanfilter.clicked.emit(False)
        self.cb_rmsfilter.setChecked(False)
        self.cb_rmsfilter.clicked.emit(False)
    def getLine(self):
        """
        @return: return the widgets associated curve
        """
        return self.plot.lines[self.idx]
    def dofilter(self,x,y):
        """
        Apply selected filter to 1Dim array a
        @param y: y: 1Dim Array
        @return: filtered Array
        """
        import time
        
        l=self.getLine()
        idx=l.buffer.idx
        
        #if self.lastidx>idx: 
        #    self.oldy=y
        #    self.lastm=np.mean(y)
        self.lastidx=idx
        t=time.time()
        
        y=self.selectedFilter(y,self.countValue//2 or 1,0x01,idx,0)#elf.lastm*self.countValue)
        
        #s=(idx-1-self.countValue)%len(y)

#         if s<=idx: 
#             y[s:idx]=np.NaN
#         else: 
#             y[s:]=np.NaN
#             y[:idx]=np.NaN
        print time.time()-t
        return x,y
    def toggleMeanFilter(self,ev):
        """
        
        Switch meanfilter on or off
        @param ev: bool wether to enable or disable
        """
        print "toggling mean filter. state=",ev
        l=self.getLine()
        try: l.preappend_filters.remove(self.selectedFilter.filterArr)
        except: pass
        for cb in [self.cb_meanfilter,self.cb_rmsfilter]:
            cb.setChecked(False)
        self.cb_meanfilter.setChecked(ev)
        
        self.meanfilter_enabled=ev
        self.enableCountControl(ev)  

        l=self.getLine()
        if ev:
            print dir(filters)
            f=filters.Meanfilter(self.countValue)
            
            self.selectedFilter=self.meanfilter=f
            l.preappend_filters.append(f.filterArr)
        #self.setFilter(ev, filters.meanfilter4)

    def setFilter(self,ev,fn):
        """
            set filter fn to state bool ev
        """
        fs=[]
        print "setFilter" ,ev,fn
        fs=self.plot.lines[self.idx].prefilters
        if ev: 
            if not self.dofilter in fs:fs.append(self.dofilter)
            self.selectedFilter=fn
        else : self.plot.lines[self.idx].prefilters.remove(self.dofilter)
    
    def toggleRMSFilter(self,ev):  
        """
        @see toggleMeanFilter:
        """
        l=self.getLine()
        try: l.preappend_filters.remove(self.selectedFilter.filterArr)
        except: pass
        for cb in [self.cb_meanfilter,self.cb_rmsfilter]:
            cb.setChecked(False)
        self.cb_rmsfilter.setChecked(ev)
        self.rmsfilter_enabled=ev
        self.enableCountControl(ev)   
        if ev:
            f=filters.RMSFilter(self.countValue)
            self.selectedFilter=f
            self.rmsfilter=f
            l.preappend_filters.append(f.filterArr)
        
        #self.setFilter(ev, lambda a,x,y,z,k: filters.meanfilter4(a**2,x,y,z,k)**0.5)#filters.rmsfilter2)     
    def handleBufferChange(self,blen):
        """
        Edit kernel widgets value on bufferchange
        """
        #oldperc=float(self.count.value())/self.count.maximum()
        #newval=int(oldperc*blen)
        self.countEdit.setMaximum(blen)
        #self.countEdit.setValue(newval)
        #self.countEdit.setSingleStep(0.01*newval)
        self.count.setMaximum(blen)
        self.countValue=self.count.value()
        #self.count.setValue(newval)
        self.count.setPageStep(0.01*blen)
    def handleCountChange(self):
        self.countEdit.setValue(self.count.value())
        self.countValue=self.count.value()
        self.ycache=None
        self.setSteps()
        self.selectedFilter.setL(self.countValue)
    def handleCountEditChange(self):
        self.count.setValue(self.countEdit.value())
        self.countValue=self.count.value()
        self.ycache=None
        self.selectedFilter.setL(self.countValue)
        self.setSteps()
    def setSteps(self):
        self.countEdit.setSingleStep(max(1,0.01*self.count.value()))
    def enableCountControl(self, b):
        self.count.setEnabled(b)
        self.countEdit.setEnabled(b)
        
    def insertValues(self,parent):
        self.fcnt+=1
        if self.fcnt<self.frameskip or not self.enabled.isChecked() or self.isHidden(): return
        self.fcnt=0
        if len(self.plot.lines)<=self.idx:return
        
        
        line=self.plot.lines[self.idx]
        buffer=line.buffer
        
#         assert isinstance(self.count, QtGui.QSlider)
#         count= int(100./self.count.value()*buffer.bufflen)
        
        value=buffer.data[buffer.idx-1]
        #print value
        assert isinstance(self.value, QtGui.QLCDNumber)
        self.value.display(value)
        self.mean.display(buffer.data.mean())
        
        self.rms.display(np.sqrt(np.mean(buffer.data**2)))
        

    
    def contextMenuEvent(self,event, *args, **kwargs):
        """
        Adds a conetextmenu with some actions        
        """
        #print args
        menu=QtGui.QMenu('x',self)
        menu.addAction(self.enabled)
        menu.addSeparator()
        lineact_group=self.linegroup
        #acs=self.acs=[]
        for i in range(len(self.plot.lines)-len(lineact_group.actions()) ):
            ac=QtGui.QAction('Line %d'%i,self)
            ac.setCheckable(True)
            lineact_group.addAction(ac)
            menu.addAction(ac)
            
        
        
        acs=lineact_group.actions()
        if len(acs)-1>=self.idx: acs[self.idx].setChecked(True)
        menu.addActions(acs)
        #self.update()
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if action in acs: self.idx=acs.index(action)
        print action
        #popup(self,self).show()
        pass
        

from .plot2 import Plot
def addWdg(plot,line):
    """
    @param Plot plot: The Plot where the line is attached
    @param line: the line this widget is responsible for
    """
    if len(plot.lines)>=LiveDataDock.id:
        makeLiveDataWidget(plot.master)
    pass

print dir(Plot.sigBufferChanged)

def makeLiveDataWidget(parent):
    
    #from qtgui import UI_Main
    #print type(parent)
    #assert isinstance(parent, UI_Main)
    dock=LiveDataDock(parent)
    parent.plot.sigLineAdded.connect(addWdg)
    #dock.setFloating(True)
    parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    #dock.hide()
    if LiveDataDock.id>2:
        for d in LiveDataDock.livewidgets[:-2]:
            parent.tabifyDockWidget(d,dock)
    return dock


from PyQt4.QtGui import QWidget,QGridLayout,QPushButton,QCursor
from PyQt4.QtCore import Qt,QPoint
class popup(QWidget):
        def __init__(self, parent = None, widget=None):    
            QWidget.__init__(self, parent)
            layout = QGridLayout(self)
            button = QPushButton("Very Interesting Text Popup. Here's an arrow   ^")
            layout.addWidget(button)

            # adjust the margins or you will get an invisible, unintended border
            layout.setContentsMargins(0, 0, 0, 0)

            # need to set the layout
            self.setLayout(layout)
            self.adjustSize()

            # tag this widget as a popup
            self.setWindowFlags(Qt.Popup)

            # calculate the botoom right point from the parents rectangle
            point        = widget.rect().bottomRight()


            # map that point as a global position
            global_point = widget.mapToGlobal(point)
            
            # by default, a widget will be placed from its top-left corner, so
            # we need to move it to the left based on the widgets width
#            self.move(global_point - QPoint(self.width(), 0))
            self.move(QCursor.pos())
            # need to set the layout
            

