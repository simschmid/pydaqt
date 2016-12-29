'''
Created on 20.11.2016

@author: simon
'''
from distutils.core import setup,Extension
from Cython.Build import cythonize

ext=Extension(name="filters",
                     sources=["filters.pyx"],
                     extra_compile_args=['-fopenmp'],
                     extra_link_args=['-lgomp','-fopenmp']
                     )
setup(
    ext_modules = cythonize([ext],annotate=True)
)