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
    def __init__(self, docname, filename, which, **kwargs):
        self.docname = docname
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

    def prepare_node(self,uri,**ctx):
        self.uri = uri
        self.path = self.doxygen.scope_to_path(self.which)
        nodes = self.doxygen.get(self.path)
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
        self.references=self.create_references(objs)
        self.context = copy.copy(self.kwargs)
        self.context["objects"] = self.references
        self.context.update(ctx)

    def render(self): 
        self.ref_register.set_uri(self.uri)
        template = self.environment.get_template(self.filename+'.html')
        return template.render(**self.context)

def visit_doxygen_node(self, node):
    x= node.render()    
    self.body.append(x)

def depart_doxygen_node(self, node):
    pass

from sphinx.util.compat import Directive
class DoxygenDirective(Directive):

    has_content = True
    def run(self):
        env = self.state.document.settings.env
        try:
            filename = self.content[0]
        except:
            raise BaseException("Please specify how you want to render the information, i.e. class/synopsis.") 

        try:
            which = self.content[1]
        except:
            raise BaseException("Please specify a class memener to document.")

        ret =  doxygen( env.docname,filename, which, **list_to_dict(self.content[2:]) )
        return [ret]

def purge_doxygen(app, env, docname):
    pass
#    env.all_doxs = [todo for todo in env.todo_all_todos
#                          if todo['docname'] != docname]


class reference_register:
    def __init__(self):
        self.uri = ""
        self._register = {}
        self._request = []
        self._production_mode = False

    def set_uri(self, uri):
        self.uri = uri

    def get_id(self, obj):
        i = None
        if hasattr(obj,"id"):
            i = obj.id
        else:
            print "Warning: object has no id."
        return i

    def production_mode(self):
        self._production_mode = True

    def create_reference(self,obj):
        i = self.get_id(obj)
        uri = "%s#%s" %(self.uri,i)
        if i in self._register and not self._production_mode:
            print "Warning: label for '%s' already exists. Skipping label creation." %i
#            return self.get_reference(obj)
        self._register[i] = uri
        return "<a name=\"%s\"></a>"%i

    def get_reference(self,obj):
        i = self.get_id(obj)
        if not i in self._request: self._request.append(i)
        if not self._production_mode:
            return "<a href=\"javascript:void(0);\">%s</a>"%obj.name
        elif not i in self._register:
            print "Warning: label not defined"
            return "<a href=\"javascript:void(0);\">%s</a>"%obj.name
        else:
            return "<a href=\"%s\">%s</a>"%(self._register[i], obj.name)

    def get_or_create_reference(self,obj):
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

    reg = reference_register()
    jenv.filters['ref'] = reg.get_reference
    jenv.filters['label'] = reg.create_reference

 #   uri = app.builder.get_relative_uri()
    for node in doctree.traverse(doxygen):
        uri =  app.builder.get_relative_uri(
            fromdocname, node.docname)

        node.ref_register = reg
        node.doxygen = dox
        node.environment = jenv
        node.prepare_node(uri)
        node.render()
#        node.relative_uri = uri
    reg.production_mode()

def setup(app):
    app.add_config_value('doxygen_xml', None, True)

    app.add_node(doxygen,
                 html=(visit_doxygen_node, depart_doxygen_node))


    app.add_directive('doxygen', DoxygenDirective)


    app.connect('doctree-resolved', process_doxygen)
    app.connect('env-purge-doc', purge_doxygen)


