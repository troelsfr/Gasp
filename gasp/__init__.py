from docutils import nodes
_ = lambda x: x
from jinja2 import Environment, PackageLoader


def list_to_dict(lst):
    nl = [q[1:].split(":",1) for q in lst if ":" in q ]
    return dict([(q[0],q[1].strip()) for q in nl])

class DoxygenNode(nodes.General, nodes.Element):    
    def __init__(self,  **kwargs):
        super(DoxygenNode,self).__init__('')
        self.__dict__.update(kwargs)

    def render(self):
        return "The render function of %s has not been overridden" % self.__class__.__name__

import copy
class reference_object:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class doxygen(DoxygenNode):
    def __init__(self, filename, which, **kwargs):
        self.filename = filename
        self.which = which

        if not "exclude" in kwargs or kwargs["exclude"].strip() == "":
            kwargs["exclude"]=[]
        else:
            exclude = [x.strip() for x in kwargs["exclude"].split(",")]
            kwargs["exclude"]=exclude

        for (a,b) in kwargs.iteritems():
            if hasattr(b,"strip") and b.strip() == "":
                kwargs[a] = True

        self.kwargs = kwargs

        super(doxygen,self).__init__(**kwargs)

    def create_references(self, objs):
        refs = []
        for o in objs:
            no = reference_object(**o.attributes)
            setattr(no,"as_string", str(o))
            if len(o.children) > 0: setattr(no,"children", self.create_references(o.children))
            refs.append(no)
        return refs

    def render(self):
        self.path = self.doxygen.scope_to_path(self.which)
        nodes = self.doxygen.get(self.path)
        template = self.environment.get_template(self.filename+'.html')
        if len(nodes) == 0:
            print "WARNING: could not find '%s'"%self.which
            return ""

        if len(self.exclude) == 0:
            objs = nodes
        else:

            objs = []
            for n in nodes:
                if not "name" in n.attributes or not n.attributes["name"] in self.exclude:
                    objs.append(n)
        refs=self.create_references(objs)
        
        kwargs = copy.copy(self.kwargs)
        kwargs["objects"] = refs
#        print kwargs
        return template.render(**kwargs)

def visit_doxygen_node(self, node):
    x= node.render()    
    self.body.append(x)

def depart_doxygen_node(self, node):
    pass

from sphinx.util.compat import Directive
class DoxygenDirective(Directive):

    has_content = True
    def run(self):
        try:
            filename = self.content[0]
        except:
            raise BaseException("Please specify how you want to render the information, i.e. class/synopsis.") 

        try:
            which = self.content[1]
        except:
            raise BaseException("Please specify a class memener to document.")

        ret =  doxygen(filename, which, **list_to_dict(self.content[2:]) )
        return [ret]

def purge_doxygen(app, env, docname):
    pass

from doxtools import DoxygenDocumentation
import glob
def process_doxygen(app, doctree, fromdocname):
    if app.config.doxygen_xml is None:
        raise BaseException("Please specify the path to the Doxygen XML in the conf.py using the variable 'doxygen_xml'.")

    env = app.builder.env

    testfiles = glob.glob("/home/tfr/Documents/Alps/build/docs/doxygen/xml/*.xml")
    print "Loading Doxygen documentation ... "
    dox = DoxygenDocumentation(testfiles)
    print "Generating Doxygen output"

    def warn(cond, msg):
        if cond: print "WARNING:",msg
    jenv = Environment(loader=PackageLoader('gasp', 'templates'))

    for node in doctree.traverse(doxygen):
        node.doxygen = dox
        node.environment = jenv

def setup(app):
    app.add_config_value('doxygen_xml', None, True)

    app.add_node(doxygen,
                 html=(visit_doxygen_node, depart_doxygen_node))


    app.add_directive('doxygen', DoxygenDirective)


    app.connect('doctree-resolved', process_doxygen)
    app.connect('env-purge-doc', purge_doxygen)


