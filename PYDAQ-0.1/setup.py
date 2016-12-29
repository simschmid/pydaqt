import sys

#from distutils.core import Extension
from setuptools.extension import Extension
from Cython.Build import cythonize
from setuptools import find_packages,setup

#from cx_Freeze import Executable,setup

exts=[Extension(name="gui.buffers",
                     sources=["gui/buffers.py"],
                     extra_compile_args=['-fopenmp'],
                     extra_link_args=['-lgomp','-fopenmp']
                     ),
      Extension(name="ctools.filters",
                     sources=["ctools/filters.pyx"],
                     extra_compile_args=['-fopenmp'],
                     extra_link_args=['-lgomp','-fopenmp']
                     ),
        Extension(name="ctools.cfilter",
                 sources=["ctools/cfilter.c"],
                 extra_compile_args=['-fopenmp'],
                 extra_link_args=['-lgomp','-fopenmp']
                 )
      ]
packages=['ctools',"devices","gui","gui.ui","plugins"]






setup(
    name="PYDAQ",
    version=0.1,
    author="Simon Schmid",
    author_email="sim.schmid@gmx.net",
    py_modules=['globals','main'],
    ext_modules = cythonize(exts,annotate=True),
    packages=packages,
    #executables=executables,
    #options=options,
    install_requires=["numpy","pyqtgraph","pyserial","pyaudio"],
    package_data={'gui.ui':"*.ui", '':"LICENSE.txt"},
    data_files=[('gui',["test.png"])],
    license="MIT"
)