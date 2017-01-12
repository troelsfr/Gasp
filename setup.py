#!/usr/bin/env python

from distutils.core import setup

setup(name='Gasp',
      version='1.0',
      description='Bridge between Doxygen and Sphinx',
      author='Troels F. Roennow',
      author_email='troels.roennow@gmail.com',
      url='https://github.com/troelsfr/Gasp',
      packages=['gasp'],
      package_data={'gasp': ['templates/*/*']},      
     )
