Gasp
====
Copyright 2012 (c) Troels F. Roennow, ETH Zurich

Gasp is a bridge between Doxygen and Sphinx allowing import of Doxygen doc in Sphinx. Gasp loads Doxygen generated XML and provides directives for including extracted docs into the reStructured text. 


How does Gasp differ from Breathe?
==================================
Breathe is a fine extension to Sphinx and has worked for me in most
cases. However, lately I wanted to use it for a different setup than
what it was designed for, and I soon realised that I had to change the
code. I always panic when I have to modify others source code if it is
any longer than 500 lines, and therefore wrote

While inspired by Breathe, Gasp differs on two crucial points:

 - It is provided with a XPath like selection langauge.
 - HTML/LaTeX/etc is seperated out of the source code such that you
   easily can customise Gasp to your needs.
 
Unlike Breathe, Gasp does not provide a fixed design which you have to
use for your project. You are rather encouraged to make your own.


Installation
============
1. Put Gasp somewhere in your Python path.
2. 
