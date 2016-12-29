'''
Created on 24.10.2016

@author: simon
'''
try:
    import matplotlib,time
    matplotlib.use('QT4Agg') 
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    from matplotlib.transforms import Bbox
except: pass
from PyQt4 import QtCore
from buffers import downsample, stretchArray
from numpy import linspace


import numpy as np

from _collections import deque
from buffers import RingBuffer
from Queue import Queue
from ctools.filters import trigger
class Trigger(object):
    def __init__(self,plot):
        self.linenumber=-1
        self.line=None
        self.edge=1 #rising:1 falling:-1
        self.value=0
        self.plot=plot
        self.trigstart=None
        self.sense=2
        self.lasty=deque(maxlen=self.sense)
        self.tmparr=None
        self.lastidx=0
    def setTreshold(self,val):
        self.sense=val
        #self.lasty.maxlen=val
        self.lasty=deque(maxlen=val)
    def setline(self,line):
        
        if line is not None:self.linenumber=self.plot.lines.index(line)
        else: self.linenumber=-1
        self.line=line
    def meanm(self):
        ms=list(self.lasty)
        #ms.append(y)
        m=0
        for i in range(self.sense-1):
            m+=(ms[i+1]-ms[i])
        
        return m/self.sense
    def inrange(self,y):
        if y>=min(self.lasty) and y<=max(self.lasty): return True
        return False
    def trigger(self,point):
        if self.line==None: return True
        y=point[self.linenumber]
        buf=self.plot.lines[0].buffer
        out=False
        if buf.maxlen-1==buf.idx: 
            self.trigstart=False
        if self.trigstart: out= True
        self.lasty.append(y)
        if not out and len(self.lasty)==self.sense and self.meanm()*self.edge>0 and self.inrange(self.value):
            self.trigstart=True
            #for l in self.plot.lines:l.buffer.idx=line.buffer.idx
            out= True
        return out
    def triggerArray(self,a,line):
        #a.dtype='f'
        #tt=time.time()
        if self.line!=line:return a
        idx=self.line.buffer.idx
        if self.trigstart and idx+len(a)>=self.line.buffer.bufflen:
            self.trigstart=False
            return a[:self.line.buffer.bufflen-idx]
        self.lastidx=idx
        if self.trigstart: return a
        if self.tmparr is not None: a=np.append(self.tmparr, a)
        out=[]
        t=trigger(a.astype('d'),self.value,self.edge,self.sense//2)
        if t is not None:
            self.trigstart=True
            out=a[t:min(self.line.buffer.bufflen,len(a))]
            if len(a)>=self.line.buffer.bufflen: self.trigstart=False
            self.tmparr=None
            self.plot.resetLinesIdx()
            
        else:
            self.tmparr=a[-self.sense:]
        #print time.time()-tt
        return out
    
    def __getstate__(self):
        d=dict(self.__dict__.items())
        del d['plot']
        del d['lasty']
        del d['line']
        del d['trigger']
        return d
class Line():
    def __init__(self,line):
        self.line=line
class Plot:
    def __init__(self,master):
        import qtgui
        assert isinstance(master, qtgui.Ui_MainWindow)
        self.samplerate=0
        self.master=master
        self.terminalEnabled=True
        self.trigger=Trigger(self)
        self.bufflen=50000
        self.current_bufflen=self.bufflen
        self.plt_block=0
        self.plt_skip=0
        self.plt_skip_count=0
        self.plt_skip_n=0
        self.record_stream=None
        self.step=1 
        self.textbuffer=deque(maxlen=1000)
        self.last_idx=0
        self.last_tf_time=time.time()
        self.transformfinished=0
        self.transformtimer=QtCore.QTimer()
        self.transform_checker_running=0
        fig=self.fig = Figure()
        ax=self.ax = fig.add_subplot(111) #: :type ax:matplotlib.axes.Axes
        fig.tight_layout()
        #line, = ax.plot(range(1000))
        ax.set_ylim(-1,1)
        canvas=self.canvas = FigureCanvasQTAgg(fig)
        canvas.show()
        ax.set_ylim(-1,1)
        master.fig.hide()
        master.gridLayout.addWidget(canvas,0,1)
        self.background = fig.canvas.copy_from_bbox(ax.bbox)
        self.bg2=None
        self.lines=[]
        self.selectedlines=set(self.lines)
        #self.ax.plot([-1,0],[0,0],clip_on=False)
        ax.set_xlim(0,10)
        canvas.draw()
        self.connectEvents()
        self.isdrawn=False
        #self.initplot()
    def connectEvents(self):
        self.lasty=None
        self.fig.canvas.mpl_connect("motion_notify_event",self.pltOnMove)
        self.fig.canvas.mpl_connect("scroll_event",self.pltOnZoom)
    def addLine(self):
        pass
    def addtxt(self,s):
        if self.terminalEnabled:self.textbuffer.append(s)
        pass
    def initplot(self,ylim=(-1,1),xlim=None ):
        xlim=xlim or (0,self.current_bufflen)
        self.plt_block=0
        self.plt_skip=0
        ax,fig,canvas=self.ax,self.fig,self.canvas
        ax.lines=[]
        self.selectedlines.clear()
        self.lines=[]
        fig.clear()
        
        ax=self.ax = fig.add_subplot(111)
        
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        #self.bg2=fig.canvas.copy_from_bbox(fig.bbox)
        ax.yaxis.set_animated(True)
        ax.xaxis.set_animated(True)
        ax.grid()
        
        canvas.draw()
        self.bg2=fig.canvas.copy_from_bbox(fig.bbox)
        ax.draw_artist(ax.yaxis)
        ax.draw_artist(ax.xaxis)
        self.canvas.blit(fig.bbox)
        
        self.bgframe=self.background = fig.canvas.copy_from_bbox(ax.bbox)
        
        self.isdrawn=True
    def resetLinesIdx(self):
        for l in self.lines: l.buffer.idx=0
    def px_to_dx(self,px):
        
        bounds=self.background.get_extents()
        bbox_xscale=bounds[2]-bounds[0]
        return px*(self.current_bufflen)/bbox_xscale
    def update_plt3(self):
        t=time.time()
        idx=self.lines[0].buffer.idx
        self.fig.canvas.restore_region(self.background)
        self.fig.canvas.restore_region(self.bgframe)

        mins=[]
        for l in self.selectedlines:
                x,y=l.buffer.getrange_sampled(0,l.buffer.bufflen,mask=False,r=int(self.ax.bbox.width))
                l.set_data((x,y))
                mins.extend((np.min(y),np.max(y)))
                self.ax.draw_artist(l) 
        print "made dat",time.time()-t
        bnds=self.ax.transData.transform([(self.last_idx,np.min(mins)),(idx,np.max(mins))])
        bnds[0,0]-=10
        bb=Bbox(bnds)
         
        print "made bb",time.time()-t
        #print self.ax.bbox.get_points()
        self.canvas.blit(bb)    
        self.bgframe= self.fig.canvas.copy_from_bbox(self.ax.bbox)
        print "made dat",time.time()-t
        self.last_idx=self.lines[0].buffer.idx
         
    def _updateplot2(self):
        
        if not self.lines:return
        try:
            if self.plt_block:return
            #return self.update_plt3()
            #fig.canvas.restore_region(background)
            #ax.draw_artist(ax.patche)
            idx=0
            last_idx=self.last_idx
            bounds=self.background.get_extents()
            #print self.ax.bbox.get_points().flatten()
            #print bounds
            self.fig.canvas.restore_region(self.background)
            cbl=self.current_bufflen
            bbox_start=bounds[0]
            bbox_scale=bounds[2]-bounds[0]
            idx=0
            idxs=[l.buffer.idx for l in self.selectedlines]
            if self.selectedlines:idx=max(idxs)#idx=lines[0].buffer.idx
            mindx=(self.current_bufflen)/bbox_scale
            startidx=(self.last_idx-7*mindx)%cbl#(bbox_scale*(last_idx-1)/cbl*mindx)%cbl
            endidx=idx#int(bbox_scale*(idx)/cbl*mindx)
            if mindx<=1: 
                last_idx=startidx=0
                endidx=cbl-1
            #print idx,startidx,endidx
            
            assert isinstance(self.ax,matplotlib.axes.Axes)
            blidx,bridx=(self.last_idx,endidx)
            nbounds,nbounds2,pbounds=None,None,None
            
            if mindx>1:
                if last_idx>endidx:
                    nbounds2=[bbox_start+endidx*bbox_scale/cbl,bounds[1],
                              bbox_start+last_idx*bbox_scale/cbl,bounds[3]]
                    self.fig.canvas.restore_region(self.bgframe,nbounds2,(bbox_start,bounds[1]))
                else:
                    nbounds=[bounds[0]-0,bounds[1], -5+bbox_start+blidx*bbox_scale/cbl,bounds[3]]
                    nbounds2=[bbox_start+10+bridx*bbox_scale/cbl,bounds[1],bounds[2],bounds[3]]
                    pbounds=Bbox.from_extents([-5+bbox_start+blidx*bbox_scale/cbl,bounds[1], bbox_start+10+bridx*bbox_scale/cbl,bounds[3]+20])
                    self.fig.canvas.restore_region(self.bgframe,nbounds2,(bbox_start,bounds[1]))
                    self.fig.canvas.restore_region(self.bgframe,nbounds,(bbox_start,bounds[1]))
                # print bounds,nbounds,nbounds2,mindx,idx,startidx
            #else: self.fig.canvas.restore_region(self.background)
            for l in self.selectedlines:
                #idx=l.buffer.idx
                #if (idx-mindx)%cbl<startidx%cbl: startidx=idx-mindx
                pxs=max(abs(startidx-endidx)/(mindx+1),100)
                x,y=l.buffer.getrange_sampled(startidx,endidx,pxs)
                
                l.set_data((x,y))
    
                self.ax.draw_artist(l)
            
            
            #if(idx<last_idx):
                #fig.canvas.restore_region(background,nbounds)
            #    pass
            #else :
            #bgframe= fig.canvas.copy_from_bbox(ax.bbox)
            
            
            #canvas.blit(fig.bbox)
            self.canvas.blit(pbounds or self.ax.bbox)
            self.last_idx=min(idxs)#idx
            self.bgframe= self.fig.canvas.copy_from_bbox(self.ax.bbox)
        #canvas.update()
            
            #canvas.flush_events()
        except RuntimeError:pass
        global updateplot_busy
        updateplot_busy=0
    def pltAppendPoint(self,line,point):
        if self.plt_skip:
            if line.skip<self.plt_skip:
                line.skip+=1
                return
        #print self.trigger.trigger(line)
       
        line.buffer.append(point)
        #line.set_ydata(list(line.buffer))
        line.skip=0
        pass
    def pltAppendPoints(self,points):
        i=0
        if self.trigger.trigger(points):
            for p in points:
                self.pltAppendPoint(self.lines[i],p)
                i+=1
    def pltAddLine(self,id=0):
        line,=self.ax.plot(range(self.current_bufflen))
        
        line.buffer=RingBuffer([0]*self.current_bufflen,maxlen=self.current_bufflen)
    #    line.buffer=RingBuffer(bufflen)
        line.skip=0
        self.lines.append(line)
    #    databuffers.append(deque([0]*bufflen,maxlen=bufflen))
        return line
    
    def pltAutoZoom(self):
        data=[]
        for l in self.selectedlines: data.extend(l.buffer)
        self.ax.set_ylim(min(data),max(data))
        self.pltAfterTransform()
    def pltAfterTransform(self,axis=0):
        """
        xaxis: axis=1
        yaxis: axis=0
        """
        
        self.ax.lines=[]
        #global background,bgframe,transformfinished,plt_block,last_tf_time
        self.transformfinished=time.time()
        self.plt_block=1
        
        if not self.transform_checker_running:
            self.transformtimer.singleShot(1,self.isTransformFinished)
            self.transform_checker_running=1
        #top.after(100, isTransformFinished)
        update_lines=1
        if time.time()-self.last_tf_time<0.02:
            update_lines=0
            print "no lup"
        if update_lines:self.last_tf_time=time.time()
        #canvas.draw(),
        #background=fig.canvas.copy_from_bbox(ax.bbox)
        #ax.lines=list(selectedlines)
        
        #bbox=getYAxis_bbox()
        self.canvas.restore_region(self.bg2)
        self.ax.grid(True)
        self.ax.draw_artist(self.ax.xaxis)
        self.ax.draw_artist(self.ax.yaxis)
        
        #canvas.blit(fig.bbox)
        self.background=self.fig.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.lines=list(self.selectedlines)
        if update_lines:
            for l in self.selectedlines:
                
                #xd,yd=l.buffer.getrange(0,self.current_bufflen)
                start=(l.buffer.idx+self.px_to_dx(10))%l.buffer.maxlen
                #xd,yd=l.buffer.getrange(start,l.buffer.idx,self.current_bufflen/500 or 1)
                #yd=downsample(l.buffer.data,int(self.ax.bbox.width))
                #xd=np.ma.arange(0,len(yd),dtype='i')*l.buffer.maxlen/len(yd)
                #self.xd_cache=xd
                #pos=l.buffer.idx/(l.buffer.maxlen/len(yd))
                #xd[pos-10:pos+10]=np.ma.masked
                #print (xd,yd)
                xd,yd=l.buffer.getrange_sampled(0,l.buffer.bufflen)
                
                if len(xd)!=len(yd): raise RuntimeError("wromg dims %d,%d"%(len(xd),len(yd)))
                
                l.set_xdata(xd)
                l.set_ydata(yd)
                self.ax.draw_artist(l)
            self.canvas.blit(self.fig.bbox)
        #background=fig.canvas.copy_from_bbox(ax.bbox)
            self.bgframe=self.fig.canvas.copy_from_bbox(self.ax.bbox)
    def isTransformFinished(self):
        self.transform_checker_running=1
        #print "checker"
        # global plt_block,transformfinished
        if time.time()-self.transformfinished>.2:
            self.plt_block=0
            self.lasty=None

            self.canvas.restore_region(self.background)
            for l in self.selectedlines:
                
                #xd,yd=l.buffer.getrange(0,self.current_bufflen)
                start=(l.buffer.idx+self.px_to_dx(10))%l.buffer.maxlen
                xd,yd=l.buffer.getrange(start,l.buffer.idx)
                #num=(len(xd)/500) or 1
                l.set_xdata(xd)
                l.set_ydata(yd)
                self.ax.draw_artist(l)
            self.canvas.blit(self.fig.bbox)
            self.bgframe=self.fig.canvas.copy_from_bbox(self.ax.bbox)
            print "tranform finished"
            self.transformfinished=0
            self.transform_checker_running=0
            return
        #self.transformfinished=time.time()
        self.transformtimer.singleShot(200,self.isTransformFinished)
        #top.after(100, isTransformFinished)
        pass
    def pltOnMove(self,ev):
        
        if ev.xdata and ev.ydata:self.master.plotMsg.setText("%.2fx%.2f"%(ev.xdata,ev.ydata))
        #self.transformfinished=0
        if ev.button != 1: return 
        lasty,ax=self.lasty,self.ax
        w,h=self.canvas.get_width_height()
        ylim=list(ax.get_ylim())
        dy=ylim[1]-ylim[0]
        delta=0
        if lasty is not None: 
            delta=(self.lasty-ev.y)*dy/h
            ylim[0]+=delta
            ylim[1]+=delta
            ax.set_ylim(ylim)
        assert isinstance(ax, matplotlib.axes.Axes)
        self.pltAfterTransform(0)
        #canvas.draw()
        #background = fig.canvas.copy_from_bbox(ax.bbox)
        self.lasty=ev.y
        #print vars(ev)
        
    def setbuffer(self,l,blen):
        #global plt_skip, plt_skip_n,step
        self.step=1
        if blen>self.bufflen:
            tmp_blen=blen
            self.plt_skip=blen/self.bufflen-1
            self.plt_skip_n=blen/(blen%self.bufflen)
            blen=self.bufflen+blen%self.bufflen
            self.step=float(tmp_blen)/blen
        else: self.plt_skip=0
        #l.set_xdata([i*self.step for i in range(blen)])
        ndata=[0]*(blen-l.buffer.maxlen)+list(l.buffer)
        l.set_ydata(ndata[:blen])
        print blen,len(ndata[:blen]),self.plt_skip,self.plt_skip_n
        l.buffer=RingBuffer(ndata[:blen],blen)
        #global current_bufflen
        self.current_bufflen=blen
        return blen
    def pltOnZoom(self,ev):
        print vars(ev)
        if ev.step <0: return self.pltOnZoomP(ev)
        else: return self.pltOnZoomM(ev)
    def pltOnZoomM(self,ev):
        limfn="ylim" if ev.y>50 else 'xlim'
        ylim=getattr(self.ax, "get_"+limfn)()
        dy=ylim[1]-ylim[0]
        if ev.y>50 :getattr(self.ax,"set_"+limfn)(ylim[0]-.1*dy,ylim[1]+.1*dy )
        else:
            self.pltZoomX(1)
        self.pltAfterTransform(0 if ev.y>50 else 1)
    
    def pltOnZoomP(self,ev):
        limfn="ylim" if ev.y>50 else 'xlim'
        ax=self.ax
        ylim=getattr(self.ax, "get_"+limfn)()
        
        dy=ylim[1]-ylim[0]
        if ev.y>50 :getattr(ax,"set_"+limfn)(ylim[0]+.1*dy,ylim[1]-.1*dy )
        else:
            self.pltZoomX(-1) 
        self.pltAfterTransform(0 if ev.y>50 else 1)
        
    def pltZoomX(self,dir):
        xlim=self.ax.get_xlim()
        dx=xlim[1]-xlim[0]
        self.ax.set_xlim(0,xlim[1]+dir*.1*dx )
        blen=int(xlim[1]+dir*.1*dx)
        self.plt_block=1
        for l in self.lines:
            self.setbuffer(l, blen)
        self.plt_block=0    
        
    def hideLine(self,line):
        self.ax.lines.remove(line)
        
        
    def showLine(self,line):
        self.ax.lines.append(line)
    
    def setXRange(self,a,b):
        self.ax.set_xlim(a,b)
        
    def poptxt(self):
        s="\n".join(self.textbuffer)
        self.textbuffer.clear()
        return s