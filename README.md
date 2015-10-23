Gasp
====
Copyright 2012 (c) Troels F. Roennow, ETH Zurich

Gasp is a bridge between Doxygen and Sphinx allowing import of Doxygen doc in Sphinx. Gasp loads Doxygen generated XML and provides directives for including extracted docs into the reStructured text. 


How does Gasp differ from Breathe?
==================================
Breathe is a fine extension to Sphinx and has worked for me in most
cases. However, lately I wanted to use it for a different setup than
what it was designed for, and I soon realised that I had to change the
code. I always panic when I have to modify others source code, if it is 
any longer than 500 lines, and therefore started writing Gasp. 

While inspired by Breathe, Gasp differs on two crucial points:

 - It is provided with a XPath like selection langauge.
 - HTML/LaTeX/etc is seperated out of the source code such that you
   easily can customise Gasp to your needs.
 
Unlike Breathe, Gasp does not provide a fixed design which you have to
use for your project. You are rather encouraged to make your own.


Quick start
===========
1. Put Gasp/gasp somewhere in your Python path.
2. Add 'gasp' to your Sphinx extension list.
3. Add "doxygen_xml" to the Sphinx configuration, and add the set this variable to the location where you have your Doxygen XML files.
4. Start using it.


Using Gasp
==========
Gasp provides two RST tags::

    .. doxygen:: [template_name]
       [namespace_selector]
       [option1]
       [option2]

and the reference tag ``dox-ref`` (TODO, still needs to be written (I think) ).

API documentation
-----------------
To add a class synopsis of the public members to 
your documentation write::

    .. doxygen:: class/synopsis
       foo::bar::class
       :public:

If you also wish to include members which has no brief
documentation string add the option ":all:". Likewise, private synopsis
page is created as::

    .. doxygen:: class/synopsis
       foo::bar::class
       :private:


In order include detailed documentation, write::

    .. doxygen:: class/members
       foo::bar::class
       :primary:
       :public:
       :private:
       :all:

The 'primary' option tells the module that this is the main place for
documentation of the class "foo::bar::class". All references to this
class will be linked here.


Concepts
--------
Gasp adds support for additional Doxygen macros. The macros are realised
through the ALIASES variable in Doxygen.
As an example one might want to add the functionality of doing concept
documentation using Boost archetypes. To this end one would need macros
to specify pre- and post conditions. This is done by adding following to
the ALIASES in doxygen.conf::

    ALIASES += "postcond=\xrefitem postcond \"Post condition\" \"Post condition\" "
    ALIASES += "precond=\xrefitem precond \"Pre condition\" \"Pre condition\" "

Gasp has a standard implementation for concept documentation (which may
be altered, if the user would like to). To see the full list of aliases
needed to be included in doxygen.conf go to the section "Standard Alias
Extension". Once the ALIASES has been enabled, one can have code
documented as:: 

    namespace concepts{
       class foo_concept {
       public:
          /***
           @brief ...
           @precond some precondition
           @postcond some postcondition
           ***/
           void bar() {}
       };

       /*** 
        @brief some free function related to the concept.
        ***/
       void bar(foo_concept &f) { };
    };

which is then included into the RST file as::

    .. doxygen:: concept/synopsis
       concepts::*

This will create a concept synopsis for
``concepts::foo_concept`` and ``concepts::bar``. (TODO: write the
synopsis template)

I don't like Gasp
-----------------
This is really sad. However, fortunately you can easily customise things
to your needs. You should take a look at the ``templates/`` folder in
the gasp directory. You can add or modify the standard templates
according to your needs, and thanks to the powerful template language of
Jinja, one can accomplish quite a few things without ever touching the
real source code.


Standard Alias Extension
========================
The standard templates in Gasp implements the following aliases::

    ALIASES += "postcond=\xrefitem postcond \"Post condition\" \"Post condition\" "
    ALIASES += "precond=\xrefitem precond \"Pre condition\" \"Pre condition\" "
    ALIASES += "new_in{1}=\xrefitem newfeature \"New feature\" \"New features\" \xmlonly <version>\1</version> \endxmlonly"
    ALIASES += "changed_in{1}=\xrefitem changed \"Changed feature\" \"Changed features\" \xmlonly <version>\1</version> \endxmlonly"
    ALIASES += "deprecated_from{1}=\xrefitem deprecated \"Deprecated feature\" \"Deprecated features\" \xmlonly <version>\1</version> \endxmlonly"

After adding this to doxygen.conf, rerun Doxygen to generate the
corresponding XML files.


Acknowledgement
===============
This project would probably not have come around if Breathe had not been
there. My sincere thanks to the author of Breathe. 

License
=======
```
Copyright (c) 2013-2015, Troels F. Roennow

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions: 

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software. 

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 
```
