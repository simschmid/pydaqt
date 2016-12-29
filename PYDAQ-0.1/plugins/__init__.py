

plugins=[]
from . import BandPass


_pluginInstances=[]




def initPlugins(app):
    print "plugins:", plugins
    for p in plugins:
        _pluginInstances.append(p(app))
    pass