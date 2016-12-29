'''
Created on 28.10.2016

@author: simon
'''
import sys
from PyQt4 import QtCore, QtGui
from ui.pydaq import *
from Dialogs import StartDialog,TriggerDialog

import devices
import plot2 as plot
from _collections import deque
import time,profile
import Dialogs as Dialogs
from terminator import run_terminatehooks

from globals import framecallbacks
from Queue import Queue,Empty

from plugins import initPlugins

app=None
class UI_Main(QtGui.QMainWindow):
    """
    The mainwindow of PyDaq
    """
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("PyDaq")
        
        self.plot=plot.Plot(self)
        self.setCentralWidget(self.ui.centralwidget)
        
        self.ui.fig.hide()

        self.buttoncmds()
        devices.plot=self.plot
        self.timer=QtCore.QTimer()
        #self.timer.timeout.connect(self.updategui)
        self.timer.singleShot(1000/30,self.updategui)
        
        #set textwidth to 100 **workaround to set initial width
        assert isinstance(self.ui.textdock0, QtGui.QDockWidget)
        self.ui.text.setMaximumSize(100,999)
        #allow expanding after 1us
        self.timer.singleShot(1,lambda: self.ui.text.setMaximumSize(9999,9999))
        self.fcnt=0
        self.ftime=time.time()
        self.framerate_correction=0
        self.active_device=None
        self.txt=deque(maxlen=50)
        self.ui.text.setMaximumBlockCount(1000)
        self.statusmsgs=self.ui.statusmsgs={}
        
        self.plotMsg=self.ui.plotMsg=QtGui.QLabel()
        self.ui.statusbar.addPermanentWidget(self.ui.plotMsg)
        self.plot.sigMouseHover.connect(
            lambda pos: self.ui.plotMsg.setText("%4.2fx%4.2f"%(pos.dataPos.x(),pos.dataPos.y()) )
            )
        
        
        self.last_selected_device=None
        self.makemenu()
        
        #self.setMaximumHeight(300)
        #self.addDockWidget(QtCore.Qt.RightDockWidgetArea, Dialogs.LiveDataDock(self))
        #self.setDockOptions(QtGui.QMainWindow.AnimatedDocks | QtGui.QMainWindow.AllowNestedDocks)
        
        Dialogs.makeLiveDataWidget(self)
        Dialogs.makeLiveDataWidget(self)
        
        self.eventQueue=self.ui.eventQueue=FunctionQueue()
        
        self.readSettings()
        initPlugins(self)
    def makemenu(self):
        """
        Creates the menubar and related actions
        """
        terminalmenu=self.menuBar().addMenu("Terminal")
        t=QtGui.QAction("Enable Terminal",self,checkable=True)
        terminalmenu.addAction(t)
        t.setChecked(True)
        def ttrigger(): self.plot.terminalEnabled=1 if t.isChecked() else 0 
        t.triggered.connect(ttrigger)
        
        self.ui.menuFile.addAction(self.rec)
        
        
        saveView=QtGui.QAction("Save Current Data",self)
        self.ui.menuFile.addAction(saveView)
        #saveView.triggered.connect(self.plot.saveCurrentData)
        
        exitact=QtGui.QAction("Exit",self)
        exitact.triggered.connect(lambda: self.close() )
        self.ui.menuFile.addAction(exitact)
    def buttoncmds(self):
        """
        configures all button actions of the app.
        """
        self.playaction=playaction=QtGui.QAction('Start', self,checkable=True)
        self.ui.toolBar.addAction(playaction)
        playaction.triggered.connect(self.pauseplay)
        
        pause=QtGui.QAction("Pause",self,checkable=True)
        self.ui.toolBar.addAction(pause)
        def pausefn():self.plot.paused^=1
        pause.triggered.connect(pausefn)
        
        self.rec=QtGui.QAction('Record', self,checkable=True)
        self.ui.toolBar.addAction(self.rec)
        self.rec.triggered.connect(self.record)
        
        self.selectlines=QtGui.QAction('Lines',self)
        self.ui.toolBar.addAction(self.selectlines)
        self.selectlines.triggered.connect(lambda:  Dialogs.SelectLines(self).show())
        
        settings=QtGui.QAction('Settings', self)
        
        #self.ui.toolBar.addAction(settings) 
        
        
        autozoom=QtGui.QAction('AutoZoom',self,checkable=True)
        def autozoomhandler():
            if autozoom.isChecked(): self.plot.enableAutorange(True)
            else: self.plot.enableAutorange(False)
            #autozoom.setEnabled(False)
        self.plot.sigAutoRangeEnabled.connect(lambda indicator: autozoom.setChecked(indicator))
        autozoom.triggered.connect(autozoomhandler)
        self.ui.plotcontrols.addAction(autozoom)       
        
        
        trigger=QtGui.QAction('Trigger',self)
        self.ui.plotcontrols.addAction(trigger)
        trigger.triggered.connect(lambda:  TriggerDialog(self).show())
        #self.ui.pauseplay.clicked.connect(self.pauseplay)
        
        fplot=QtGui.QAction("Fourier",self,checkable=True)
        self.ui.plotcontrols.addAction(fplot)
        fplot.triggered.connect(lambda: self.plot.enableFFT(True if not self.plot.fouriermode else False))#Dialogs.Fourierplot(self).show())
        
        logx=QtGui.QAction("LogX",self,checkable=True)
        self.ui.plotcontrols.addAction(logx)
        logx.toggled.connect(lambda ev:self.plot.setLog(ev,None))

        logy=QtGui.QAction("LogY",self,checkable=True)
        self.ui.plotcontrols.addAction(logy)
        logy.toggled.connect(lambda ev:self.plot.setLog(None,ev))
        
        appendRolling=QtGui.QAction("RollX",self,checkable=True)
        self.ui.plotcontrols.addAction(appendRolling)
        appendRolling.toggled.connect(self.plot.setBuffersRolling)
        
        pass
    def pauseplay(self,ev):
        """
        Stops a running device or opens a dialog for starting a new device.
        @param ev: bool False to stop else start 
        """
        if self.active_device:
            self.active_device._disable()
            self.active_device=None
            self.plot.isdrawn=False
            
            return
        print "klick"
        d=StartDialog(self,self.last_selected_device)
        d.show()
        #self.last_selected_device=d.selected_device
        print "after startdialog window opened" , self.last_selected_device
        return
#         ui.devices_cbox.addItem('Please Select')
#         for dev in devices.devices: ui.devices_cbox.addItem(dev.name)
#         ui.devices_cbox.currentIndexChanged.connect(self.select_dev)
#         d.show()
    
    def record(self):
        """
        starts a data record to a file. if no record is actve, a file-dialog will pop up, else
        the record will stop
        """
        from os.path import expanduser
        assert isinstance(self.active_device, devices.DeviceBase)
        if not self.active_device.record:
            home = expanduser("~")
            d=QtGui.QFileDialog()
            d.setDirectory("/home/")
            fname=d.getSaveFileName(None,"Record Data",home,"Comma Separated Values (*.csv)")
            if fname: 
                self.rec.setText("Stop")
                self.active_device.record=open(str(fname),"w")
                print fname
        else:
            self.active_device.record=None
            if isinstance(self.active_device.record, file):self.active_device.record.close()
            self.rec.setText("Record")
        if not self.active_device.record: self.rec.setChecked(False)
        
    def updategui(self):
        """
        updates gui with a rate of 50/s. custom jobs can be appended to framecallbacks
        """
        self.timer.singleShot(max(1000./50+self.framerate_correction,0),self.updategui)
        self.fcnt+=1
        t=time.time()
        if t-self.ftime>=1:
            frate=self.fcnt/(t-self.ftime)
            self.fcnt=0
            self.ftime=t
#             diff=frate-1000./30
#             if diff: 
#                 #self.framerate_correction+=float(diff)/2
#                 print "frameratecorrecting:",self.framerate_correction ,diff
            
            self.ui.statusmsgs['fps']="fps: %d"%frate
            self.ui.statusbar.showMessage(' '.join(self.ui.statusmsgs.values()))
        if self.plot.textbuffer: 
            self.ui.text.appendPlainText(self.plot.poptxt())
            #self.plot.textbuffer.clear()
        if self.plot.isdrawn: 
            t=time.time()
            self.plot._updateplot2()
   #         print "udateplot",time.time()-t
        self.run_framecallbacks()
        
        #run events
        try: 
            self.ui.eventQueue.get(False)
        except Empty: pass
    def run_framecallbacks(self):
        """
        run callbacks which are stored in module globals.framecallbacks
        """
        for v in framecallbacks.values(): v(self)
        
        
    def closeEvent(self, *args, **kwargs):
        """
        When closing mainWindow, Save some App-related data like geometry, dockstates etc...
        """
        settings=QtCore.QSettings("sims","pydaq")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        print "saving gui"
        return QtGui.QMainWindow.closeEvent(self, *args, **kwargs)
    
    def readSettings(self):
        settings=QtCore.QSettings("sims","pydaq")
        self.restoreGeometry(settings.value("geometry").toByteArray())
        self.restoreState(settings.value("windowState").toByteArray())
        
def delrows(qtext,rows):
    cursor = qtext.textCursor()
    cursor.select(QtGui.QTextCursor.BlockUnderCursor)
    cursor.removeSelectedText()
    cursor.deleteChar()
    
class FunctionQueue(Queue):
    """
    A Queue implementation for functions (jobs) 
    Put a function alonside some args:
        fq=FunctionQueue()
        fq.put(lambda x:x^2,(34,))
    Somewhere else the function may be executed:
        fq.get()
    
    methods:
        put(fn,args,block,timeout):
            fn: Afunction to execute
            args: (optional) The arguments to apply to fn as tuple
            block: block until queue has space, else raise Full
            timeout: block for max seconds, else raise
            
        get([block,timeout]):
            execute a fucntion with args as delivered by put
    """
    def get(self, block=True, timeout=None):
        tpl=Queue.get(self, block=block, timeout=timeout)
        print tpl
        if isinstance(tpl, tuple):
            fn,args=tpl
            fn(*args)
        else: tpl()
    def put(self, fn,args=None, block=True, timeout=None):
        args=tuple(args or [])
        Queue.put(self, (fn,args), block=block, timeout=timeout)
        

def startapp():
    devices.init_devices()
    app = QtGui.QApplication(sys.argv)
    myapp = UI_Main()
    myapp.show()
    
    status=app.exec_()
    run_terminatehooks()
    import multiprocessing as mp, time
    #time.sleep(5)
    print mp.active_children()
    sys.exit(status)
    
if __name__ == "__main__":
    startapp()

