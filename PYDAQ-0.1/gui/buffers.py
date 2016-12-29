'''
Created on 26.10.2016

@author: simon
'''
import numpy as np
from array import array
from threading import Lock
from numpy import linspace
import time 
try: 
    import cython

    if cython.compiled:
        print("Using Compiled buffers")

except: pass

  
class RingBuffer:
    """
    Threadsafe Ringbuffer implementattino with numpy arrays
    """ 
    def __init__(self,init=None,maxlen=1000,dtype='f',masked=True):
        #self.data=np.array([0]*bufflen,dtype=dtype)
        bufflen=maxlen
        self.data=np.array(array('f',[0]*bufflen))
        if masked: self.xdata=np.ma.arange(bufflen)
        else: self.xdata=np.arange(bufflen)
        self.masked=masked 
        self.mask=np.ones(bufflen,'i')
          
        self.idx=0 
        self.bufflen=bufflen
        self.maxlen=bufflen
        self.lock=Lock()
        self.rolling=False
        
    def append(self,val,lock=True):
        if lock: self.lock.acquire()
        if self.rolling: self.appendRolling(val)
        else: self.appendRinging(val)
        if lock: self.lock.release() 
        # print self.data
    def appendRolling(self,val):
        self.data[:-1]=self.data[1:]
        self.data[-1]=val
    def appendRinging(self,val):
        self.data[self.idx]=val
        self.idx=(self.idx+1)%self.bufflen
    
    def appendmulti(self,arr,align=None):
        """
        if align is set to 1 and index reaches bufflen, discard  remaining data 
        """  
        if self.rolling:return self.appendMultiRolling(arr)
        self.lock.acquire()
        buf=self.data 
        start=self.idx 
        lmax=self.bufflen-start
        if len(arr)>self.bufflen:
            arr=arr[-self.bufflen:]
        l=len(arr)
        arr=np.array(arr,'f')
        #print len(buf),l
        if l<=lmax: buf[start:start+l]=arr[:l]
        elif align is None: 
            buf[start:]=arr[:lmax]
            buf[:l-lmax]=arr[lmax:]
        elif align==1:
            l=lmax
            buf[start:]=arr[:lmax]
        self.idx=(start+l)%self.bufflen 
        self.lock.release()
        
    def appendMultiRolling(self,arr,align=None):
        self.lock.acquire()
        arr=arr[-self.bufflen:]
        l=len(arr)
        self.data[:self.bufflen-l]=self.data[l:]   
        self.data[-l:]=arr
        self.lock.release()
    
    def __iter__(self):
        return self.data.__iter__()
    def __array__(self,x): return self.data
    def resize(self,len):
        self.lock.acquire()
        ndata=np.copy(self.data)
        ndata.resize(len)
        self.data=ndata
        self.idx=min(self.idx,len-1)
        self.mask=np.ones(len,'i')
        self.bufflen=len
        self.maxlen=len
        if self.masked: self.xdata=np.ma.arange(len)
        else: self.xdata=np.arange(len)
        self.lock.release() 
    def getrange(self,a,b,step=1,masked=True):
        #self.lock.acquire()
        ax,bx=sorted((a,b))
        if a>b: 
            #print a,b
            #xdata=np.ma.array(np.append(np.arange(0,ax,step,'i'),np.arange(bx,self.bufflen,step,'i')))

            #ydata=downsample(np.append(self.data[:ax] ,self.data[(bx%self.bufflen):]),self.maxlen/step)
      
            xdata=np.append(self.xdata[:ax:step],self.xdata[bx::step])
            if self.masked: xdata[ax/step]=np.ma.masked
            
            #print len(xdata),len(ydata)
            #out=(xdata,ydata[:len(xdata)])
            out= (xdata
                     ,np.append(self.data[:ax:step] ,self.data[(bx%self.bufflen)::step]))
            
            
#             return (np.append(np.arange(bx,self.bufflen),np.arange(ax))
#                     ,np.append(self.data[(bx%self.bufflen):] ,self.data[:ax] ))
        else: 
            #xdata=np.ma.array(np.arange(a,b,step,'i'))
            xdata=self.xdata[a:b:step]
            #xdata[(b-a-1)/step]=np.ma.masked
            if self.masked and self.idx>=a and self.idx<b:
                xdata[(self.idx-a)/step]=np.ma.masked
            out= (xdata,self.data[a:b:step])
            #out= (xdata,downsample(self.data[a:b],self.maxlen/step))
        
        #self.lock.release()
        return out
    def getrange_sampled(self,a,b,r=500,mask=True):
        if a<=b:
            y=downsample(self.data[a:b],r)
            x=np.linspace(a,b-1,len(y))
            step=self.bufflen/len(y)
            if mask:x=np.ma.masked_inside(x,self.idx,self.idx-step)
            return (x,y)
        else: #return self.getrange(a, b)
            y=np.append(self.data[:b] ,self.data[(a%self.bufflen):])
            y=downsample(y,r)
            step=self.bufflen/len(y)
            x=downsample(np.append(self.xdata[:b],self.xdata[a:]),r)
            x=np.ma.masked_inside(x,b,b-step)
            return (x,y)

def stretchArray(a,num2):
    num=len(a)
    fac=float(num2)/num
    outa=np.zeros(num2)
    j=0
    i=0
    if fac>=1:
        while j<num:
            ilim=fac*j
            while i<=ilim+1 and i<num2:
                outa[i]=a[j]
                i+=1
            j+=1
    else:
        while j<num2:
            while i*fac<=j:
                i+=1
            outa[j]=a[i]
            j+=1
               
    return outa
from multiprocessing import Pool,Process,Queue
#pool=Pool(4)


def downsample(a,r=500,f1=np.nanmax,f2=np.nanmin):
    
    nlen=len(a)/r
    if not nlen: return a
    npad=len(a)%nlen
    if  npad:
        a=np.append(np.zeros((nlen-npad))*np.NaN,a )
    b=a.reshape(-1,nlen)
    out=np.vstack((f2(b,axis=1),f1(b,axis=1))).reshape(-1,1,order='F').flatten()
    return out

    #return out[-2*r:]
     
# 
# def do(qin,qout):
#     while 1:
#         a=qin.get()
#         out=downsample(*a)
#         qout.put(out)
# 
# qin=Queue()
# qout=Queue()
# ps=[Process(target=do,args=(qin,qout)) for i in range(4)]
# [p.start() for p in ps]
# 
# def getsub(arr):
#     a=[]
#     num=1
#     step=len(arr)/num
#     
#     
#     for i in xrange(num):
#         pos1=i*step
#         pos2=(i+1)*step    
#         qin.put( (arr[pos1:pos2],500/num))
#     #print a
#     
#     out=[]
#     for i in xrange(num):
#         newa=qout.get()
#         out.append(newa)
#     out=np.array(out).flatten()
#     return out
        
#import matplotlib as plt
import matplotlib
#matplotlib.use('QT4agg') 
from matplotlib import pyplot as plt

import sys
if __name__=="__main__":
    from time import time
    t=time()
    num=100000
    r=2000
    x=np.linspace(0, 1,num)    
    a=1*np.sin(2*np.pi*x*10)
    print "gen data in",time()-t
    t=time()
    stretchArray(a, 500)
    print "stretchin in ",time()-t

    t=time()
    data=downsample(a, r)
    print "downsampled in",time()-t
    xdata=np.linspace(0,1,len(data))
    t=time()
    plt.plot(xdata,data)
    plt.savefig("test2.png")
    print "plotted in %f"%(time()-t)
    #sys.exit(0)
    plt.close()
    plt.ion()
    fig=plt.figure()    
    ax=fig.add_subplot(2,1,1)
    ax.set_ylim(-1.5,2.5)
    ax2=fig.add_subplot(2,1,2)
    ax2.set_ylim(-1.5,2.5)
    
    #plt.ion()
    fig.show()
    #fig.show()
    #fig.show()
    fig.canvas.draw()
    
    background = fig.canvas.copy_from_bbox(ax.bbox)
    t=time()

    
    b= downsample(a, r)
    x2=np.linspace(0,1,2*r)#downsample(x, r)
    l,=ax.plot(x2,b)  
    ax.draw_artist(l)
    fig.canvas.draw()
    print "t=",time()-t
    t=time()
    l2,=ax2.plot(x,a)
    ax2.draw_artist(l2)
    fig.canvas.blit(ax2.bbox)
    fig.canvas.draw()
    print "t=",time()-t,len(x),len(a),len(x2),len(b)
    t=time()
    #l.set_animated(True)
    import time
    #fig.set_animated(True)


    step=len(a)*0.005
    tmp=np.zeros(len(a))
    while 1:
        #time.sleep(0.02)
        fig.canvas.restore_region(background)
        print 1./(time.time()-t)
        t=time.time()
        #a=np.append(a[-step:],a[:-step])
        tmp[:step]=np.random.normal(0,.1,step)
        #tmp[:step]=a[-step:]
        tmp[step:]=a[:-step]
        a=tmp
        print "making arr", time.time()-t
        l.set_data((x2,downsample(tmp,r)))
        print "sampling data", time.time()-t
        #l.set_data((x2,downsample(a, r)))
        ax.draw_artist(l)
        fig.canvas.blit(ax.bbox)
        fig.canvas.start_event_loop(.001)
        #print "plotted",time.time()-t
        
    print "plt took" 
    
    #while 1:
    #    plt.pause(.1)
    raw_input("press")
    
