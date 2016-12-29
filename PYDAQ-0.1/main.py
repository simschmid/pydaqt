#!/user/bin/python
'''
Created on 24.10.2016

@author: simon
'''


import gui.qtgui as gui
def start():    
    print __file__
    import os
    print "Director is:", os.getcwd()
    os.chdir(os.path.dirname(__file__))
    gui.startapp()
#print "plaplaplpal"
#start()
if __name__ == '__main__':
    

    gui.startapp()
    pass