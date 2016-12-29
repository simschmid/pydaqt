'''
Created on 24.10.2016

@author: simon
'''
import tkSimpleDialog
from threading import Thread
from traceback import print_exc

bufflen=50000
current_bufflen=bufflen
plt_skip=0
plt_skip_count=0
plt_skip_n=0
record_stream=None
step=1 

from Tkinter import *
import matplotlib
matplotlib.use('GTKAgg') 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

#from collections import deque
from buffers import RingBuffer as deque
from collections import deque as realdeque
import buttons
import numpy as np,time


top=Tk()
top.wm_title("PyDAQ")
listcontainer=Frame(top)
listcontainer.pack(side="top")
Lb1 = Frame(listcontainer)#,orient=VERTICAL)

footer=Frame(top,relief='sunken',borderwidth=2)
footer.pack(side='bottom',fill=X)
flabel=Label(footer,text="by simschmid",anchor=W)
flabel.pack(side='left',expand=1,fill=BOTH)
fpsvar=StringVar(value="fps:")
fpslabel=Label(footer,textvariable=fpsvar)
fpslabel.pack(side='right')

pltframe=Frame(Lb1)
pltframe.pack(side="right",fill=BOTH,expand=1)
txt=Text(Lb1,width=30)

txt.insert(END, "tests")
txtbuff=realdeque(maxlen=50)

txt.pack(side='left',fill='both', expand=1)
Lb1.pack(fill=BOTH,expand=1)
listcontainer.pack(fill=BOTH,expand=1)

fig = Figure()
ax = fig.add_subplot(111) #: :type ax:matplotlib.axes.Axes
#line, = ax.plot(range(bufflen))
#line.buffer=deque([0]*bufflen,maxlen=bufflen)
#line.skip=0
ax.set_ylim(-1,1)
canvas = FigureCanvasTkAgg(fig,master=pltframe)
canvas.show()

vline=None
selectedlines=set(list([]))
# ax.set_ylim(-1,1)
# ax.set_xlim(0,bufflen)
canvas.get_tk_widget().pack(side='top', fill='both', expand=1)


# background = fig.canvas.copy_from_bbox(ax.bbox)
bg2=None

def initplot():
    global fig,canvas,ax,lines,plt_skip,background,vline,bgframe,bg2
    plt_skip=0
    ax.lines=[]
    selectedlines.clear()
    lines=[]
    fig.clear()
    ax = fig.add_subplot(111)
    
    ax.set_xlim(0,current_bufflen)
    ax.set_ylim(-1,1)
    ax.yaxis.set_animated(True)
    ax.xaxis.set_animated(True)
    ax.grid()
    
    canvas.draw()
    bg2=fig.canvas.copy_from_bbox(fig.bbox)
    ax.draw_artist(ax.yaxis)
    ax.draw_artist(ax.xaxis)
    canvas.blit(fig.bbox)
    bgframe=background = fig.canvas.copy_from_bbox(ax.bbox)
    
    #vline,=ax.plot([10,10],[-1,1])
    
    #canvas.draw()
initplot()
def pltOnLeftDrag(ev):
    #print vars(ev)
    pass
#canvas.get_tk_widget().bind('<Motion>', pltOnLeftDrag)  

plt_block=0
updateplot_busy=0
def updateplot():
    global updateplot_busy
    if not updateplot_busy: 
        updateplot_busy=1
        top.after_idle(_updateplot)
        
last_idx=0
bgframe=None
tframe=time.time()
fcnt=0
def _updateplot():
    global bgframe,last_idx,fcnt,tframe

    return _updateplot2()
    if not lines:return
    
    try:
        if plt_block:return
        
        fig.canvas.restore_region(background)
        #ax.draw_artist(ax.patche)
        
        idx=0
        for l in selectedlines:
            idx=l.buffer.idx
            l.set_ydata(l.buffer.data)
            #l.set_ydata(l.buffer.data[last_idx:idx])
            #l.set_xdata(range(last_idx,idx))
            ax.draw_artist(l)
            #bgframe= fig.canvas.copy_from_bbox(ax.bbox)
        #if(idx<last_idx):fig.canvas.restore_region(background)
        #else : fig.canvas.restore_region(bgframe)
        canvas.blit(ax.bbox)
        last_idx=idx
    #canvas.update()
        
        #canvas.flush_events()
    except RuntimeError:pass
    global updateplot_busy
    updateplot_busy=0
    
def _updateplot2():
    global bgframe,last_idx,ax,background
    if not lines:return
    try:
        if plt_block:return
        
        #fig.canvas.restore_region(background)
        #ax.draw_artist(ax.patche)
        idx=0
        bounds=background.get_extents()
        fig.canvas.restore_region(background)
        cbl=current_bufflen
        bbox_start=bounds[0]
        bbox_scale=bounds[2]-bounds[0]
        idx=0
        idxs=[l.buffer.idx for l in selectedlines]
        if lines:idx=max(idxs)#idx=lines[0].buffer.idx
        mindx=(current_bufflen)/bbox_scale
        startidx=(last_idx-7*mindx)%cbl#(bbox_scale*(last_idx-1)/cbl*mindx)%cbl
        endidx=idx-2#int(bbox_scale*(idx)/cbl*mindx)
        if mindx<=1: 
            last_idx=startidx=0
            endidx=cbl-1
        #print idx,startidx,endidx
        
        assert isinstance(ax,matplotlib.axes.Axes)
        blidx,bridx=(last_idx,endidx)
        nbounds,nbounds2=None,None
        if mindx:
            if last_idx>endidx:
                nbounds2=[bbox_start+endidx*bbox_scale/current_bufflen,bounds[1],
                          bbox_start+last_idx*bbox_scale/current_bufflen,bounds[3]]
                fig.canvas.restore_region(bgframe,nbounds2,(bbox_start,bounds[1]))
            else:
                nbounds=[bounds[0]-10,bounds[1], -5+bbox_start+blidx*bbox_scale/current_bufflen,bounds[3]]
                nbounds2=[bbox_start+10+bridx*bbox_scale/current_bufflen,bounds[1],bounds[2],bounds[3]]
                fig.canvas.restore_region(bgframe,nbounds2,(bbox_start,bounds[1]))
                fig.canvas.restore_region(bgframe,nbounds,(bbox_start,bounds[1]))
            # print bounds,nbounds,nbounds2,mindx,idx,startidx
        else: fig.canvas.restore_region(background)
        for l in selectedlines:
            #idx=l.buffer.idx
            #if (idx-mindx)%cbl<startidx%cbl: startidx=idx-mindx
            l.set_data(l.buffer.getrange(startidx,endidx))

            ax.draw_artist(l)
        
        
        #if(idx<last_idx):
            #fig.canvas.restore_region(background,nbounds)
        #    pass
        #else :
        #bgframe= fig.canvas.copy_from_bbox(ax.bbox)
        
        
        #canvas.blit(fig.bbox)
        canvas.blit(ax.bbox)
        last_idx=min(idxs)#idx
        bgframe= fig.canvas.copy_from_bbox(ax.bbox)
    #canvas.update()
        
        #canvas.flush_events()
    except RuntimeError:pass
    global updateplot_busy
    updateplot_busy=0
def resizeplot(xlim=0,ylim=0):
    #todo: implement this fn to all methods which changes limits of plot
    #if plt_block:return
    canvas.draw()
    #background = fig.canvas.copy_from_bbox(ax.bbox)


def pltOnZoomP(ev):
    limfn="ylim" if ev.y<450 else 'xlim'
    ylim=getattr(ax, "get_"+limfn)()
    
    dy=ylim[1]-ylim[0]
    if ev.y<450 :getattr(ax,"set_"+limfn)(ylim[0]+.1*dy,ylim[1]-.1*dy )
    else:
        getattr(ax,"set_"+limfn)(0,ylim[1]-.1*dy )
        blen=int(ylim[1]-.1*dy)
        plt_block=1
        for l in lines:
            setbuffer(l, blen)
        plt_block=0     

    print vars(ev)   
    pltAfterTransform(0 if ev.y<450 else 1)
def pltOnZoomM(ev):
    limfn="ylim" if ev.y<450 else 'xlim'
    ylim=getattr(ax, "get_"+limfn)()
    dy=ylim[1]-ylim[0]
    if ev.y<450 :getattr(ax,"set_"+limfn)(ylim[0]-.1*dy,ylim[1]+.1*dy )
    else:
        getattr(ax,"set_"+limfn)(0,ylim[1]+.1*dy )
        blen=int(ylim[1]+.1*dy)
        plt_block=1
        for l in lines:setbuffer(l, blen)
        plt_block=0  
    print vars(ev)   
    pltAfterTransform(0 if ev.y<450 else 1)
def setbuffer(l,blen):
    global plt_skip, plt_skip_n,step
    step=1
    if blen>bufflen:
        tmp_blen=blen
        plt_skip=blen/bufflen-1
        plt_skip_n=blen/(blen%bufflen)
        blen=bufflen+blen%bufflen
        step=float(tmp_blen)/blen
    else: plt_skip=0
    l.set_xdata([i*step for i in range(blen)])
    ndata=[0]*(blen-l.buffer.maxlen)+list(l.buffer)
    l.set_ydata(ndata[:blen])
    print blen,len(ndata[:blen]),plt_skip,plt_skip_n
    l.buffer=deque(ndata[:blen],blen)
    global current_bufflen
    current_bufflen=blen
    return blen

lasty=None
def pltOnMove(ev):
    global lasty,ax
    w,h=canvas.get_width_height()
    ylim=list(ax.get_ylim())
    dy=ylim[1]-ylim[0]
    delta=0
    if lasty is not None: 
        delta=(ev.y-lasty)*dy/h
        ylim[0]+=delta
        ylim[1]+=delta
        ax.set_ylim(ylim)
    #global background
    assert isinstance(ax, matplotlib.axes.Axes)
    pltAfterTransform(0)
    #canvas.draw()
    #background = fig.canvas.copy_from_bbox(ax.bbox)
    lasty=ev.y
    print vars(ev)
def pltOnMoveStop(ev):
    global lasty
    lasty=None
def pltOnZoom(ev):
    print ev
    if ev.delta <0: return pltOnZoomP(ev)
    else: return pltOnZoomM(ev)
tkcanvas=canvas.get_tk_widget()
tkcanvas.bind("<Button-5>",pltOnZoomP)
tkcanvas.bind("<Button-4>",pltOnZoomM)
tkcanvas.bind_all("<MouseWheel>",pltOnZoom)
tkcanvas.bind("<B1-Motion>", pltOnMove)
tkcanvas.bind("<ButtonRelease-1>",pltOnMoveStop)
lines=[]
databuffers=[deque(maxlen=bufflen) ]

transformfinished=1
def isTransformFinished():
    global plt_block,transformfinished
    if transformfinished:
        plt_block=0
        return
    transformfinished=1
    top.after(100, isTransformFinished)
    pass
last_tf_time=time.time()
def pltAfterTransform(axis=0):
    """
    xaxis: axis=1
    yaxis: axis=0
    """
    
    ax.lines=[]
    global background,bgframe,transformfinished,plt_block,last_tf_time
    transformfinished=0
    plt_block=1
    top.after(100, isTransformFinished)
    update_lines=1
    if time.time()-last_tf_time<0.05:
        update_lines=0
        print "no lup"
    if update_lines:last_tf_time=time.time()
    #canvas.draw()
    #background=fig.canvas.copy_from_bbox(ax.bbox)
    #ax.lines=list(selectedlines)
    
    #bbox=getYAxis_bbox()
    canvas.restore_region(bg2)
    ax.grid(True)
    ax.draw_artist(ax.xaxis)
    ax.draw_artist(ax.yaxis)
    
    #canvas.blit(fig.bbox)
    background=fig.canvas.copy_from_bbox(ax.bbox)
    ax.lines=list(selectedlines)
    if update_lines:
        for l in lines:
            
            xd,yd=l.buffer.getrange(0,current_bufflen)
            num=(len(xd)/500) or 1
            l.set_xdata(xd[::num])
            l.set_ydata(yd[::num])
            ax.draw_artist(l)
    canvas.blit(fig.bbox)
    #background=fig.canvas.copy_from_bbox(ax.bbox)
    bgframe=fig.canvas.copy_from_bbox(ax.bbox)
def getYAxis_bbox():
    yaxis=ax.yaxis
    assert isinstance(yaxis, matplotlib.axis.YAxis)
    tmp=np.ndarray.flatten(yaxis.get_tightbbox(canvas.renderer).get_points())
    bbox=bg2.get_extents()
    bbox=[bbox[0],bbox[1],tmp[2],tmp[3]]
    return np.array(bbox)
def pltAddLine(id):
    line,=ax.plot(range(current_bufflen))
    
    line.buffer=deque([0]*current_bufflen,maxlen=current_bufflen)
#    line.buffer=RingBuffer(bufflen)
    line.skip=0
    lines.append(line)
#    databuffers.append(deque([0]*bufflen,maxlen=bufflen))
    return line

def pltAppendPoint(line,point):
    global plt_skip_count
    if plt_skip:
        if line.skip<plt_skip:
            line.skip+=1
            return
    line.buffer.append(point)
    #line.set_ydata(list(line.buffer))
    line.skip=0
    pass

def pltAutoZoom():
    data=[]
    for l in lines: data.extend(l.buffer)
    ax.set_ylim(min(data),max(data))
    pltAfterTransform()
    #canvas.draw()
update_txt_busy=0
def addtxt(txt):
    txtbuff.append(txt)
def update_txt(data):
    global update_txt_busy
    if not update_txt_busy:
        update_txt_busy=1
        top.after_idle(_update_txt,data)
def _update_txt(data):
    global update_txt_busy
    update_txt_busy=1
    txt.insert("1.0",data)
    txt.delete('50.0', END)
    update_txt_busy=0

def gui_updater(framerate=1000/30):
    global bgframe,last_idx,fcnt,tframe
    fcnt+=1
    tnow=time.time()
    if tnow-tframe>2:
        fpsvar.set("fps:%2d"%(fcnt/(tnow-tframe)))
        tframe=tnow
        fcnt=0
    top.update_idletasks()
    top.after(framerate, gui_updater,framerate)
    
    _updateplot()
    
    if txtbuff:
        _update_txt(''.join(txtbuff))
        txtbuff.clear()
   
def gui_updater_thread(framerate=1000/30):
    while 1:
        try:
            time.sleep(1.*framerate/1000)
            _updateplot()
            if txtbuff:
                _update_txt(''.join(txtbuff))
                txtbuff.clear()
        except: print_exc()
class pltSelectLinesDialog(tkSimpleDialog.Dialog):
    def body(self,master):
        self.wm_title("Select Lines")
        lb=Listbox(master,selectmode=EXTENDED)
        for i in range(len(lines)):
            lb.insert(END,str(i))
            if lines[i] in selectedlines:lb.selection_set(i, i)
        #lb.selection_set(0, END)
        lb.pack()
        self.lb=lb
        pass
    def apply(self):
        items = map(int, self.lb.curselection())
        ax.lines=[]
        global lines
        #slines=set([lines[i] for i in items])
        selectedlines.clear()
        for i in items:
            selectedlines.add(lines[i])
            ax.lines.append(lines[i])
            



buttons.makebuttons(pltframe)
# tgui=Thread(target=gui_updater_thread)
# tgui.daemon=True
# tgui.start()
import sys
frate=1000/30
if 'win' in sys.platform: 
    print "platform is ",sys.platform
    frate=5
gui_updater(frate)
#w=Canvas(Lb1,width=600,height=300)
#w.pack(side='right')
if __name__ == '__main__':
    mainloop()
    pass
