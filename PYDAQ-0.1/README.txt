Beschreibung

PyDaq ist ein Programm zur Datenaquisition und Liveanzeige aus verschiedenen Quellen. Die Daten\
 können live aufgezeichnet werden. 
 
 Quellen:
    Serial Port:    Empfang von Komma-Serparierten Werten z.B. "1.23,22.1,233.1"
    Audio:          Eingänge der Soundkarte. Pegel werden als Ganzzahlen aufgezeichnet
    
weitere Features:
    Meanfilter: Glättung der Daten in einem bestimmten Radius
    RMS-Filter: Wie Meanfilter, RMS eben.
    Fourier:    Live FourierAnalyse.
    Logscaling: Logarithmische Skalierung der Koordinatenachsen
    
Installation    
    1. first install: python setuptools, Cython, Qt4
    2. run setup.py install
    3. run pydaq
    


LICENSE:

Copyright (c) 2016 Simon Schmid | sim.schmid@gmx.net

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    