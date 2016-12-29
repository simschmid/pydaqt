"""Constants Defined in filter"""

import ctypes
from numpy.ctypeslib import ndpointer
import os 
import time

import numpy as np

from . import filters
print "loading package ctools"
#from ctools import filters

filters.fmode_normal=0x00
filters.fmode_circular=0x01

# 
# print dir(filters)
# 
# dir_path = os.path.dirname(os.path.realpath(__file__))
# 
# lib=ctypes.cdll.LoadLibrary(os.path.join(dir_path,"cfilter.so"))
# 
# _meanf=lib.meanf
# _meanf.argtypes = [ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
#                 ctypes.c_int,
#                 ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
#                 ctypes.c_int]
# def meanfilter(a,r):
#     a=np.asarray(a, dtype=np.double)
#     out=np.empty(a.shape,dtype=np.double)
#     _meanf(a,len(a),out,r)
#     return out
# 
# def pmeanfilter(a,r):
#     out=np.empty_like(a)
#     l=len(a)
#     for i in xrange(l):
#         mean=0
#         for j in xrange(i,min(l,i+r)):
#             mean+=a[j]
#         out[i]=mean/r
#     return out

# if __name__=='__main__':
#     x=np.sin(np.arange(500000,dtype=np.double))
#     print x
#     t=time.time()
#     print meanfilter(x, 500)
#     print time.time()-t
#     print "test"