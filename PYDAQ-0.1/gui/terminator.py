'''
Created on 27.10.2016

@author: simon
'''
terminatehooks=[]
def run_terminatehooks():
    print "running termination methods"
    for h in terminatehooks: h()