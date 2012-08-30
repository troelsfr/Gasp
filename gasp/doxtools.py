from xml.dom import minidom


class Node:
    def __init__(self, partial_path, children = None):
        self.partial_path = partial_path
        self.children = []
        if children is not None:
            self.children = children
            for c in children:
                c.parent = self

        self.parent = None
        self.attributes = {}

    def get(self,path):
        if self.partial_path == path or path=="*":
            return [self]
        try:
            lhs, rhs = path.split("/",1)
        except:
            return []

        if self.partial_path == lhs or lhs == "*":
            rets = []
            for c in self.children:
                rets += c.get(rhs)
            return rets

        return []

    def get_or_create(self, path):
        ret = self.get(path)
        if len(ret) > 0: return ret

        return self.create(path)



    def create(self, path):
        try:
            lhs, rhs = path.split("/",1)
            if self.partial_path == lhs or lhs == "*":
                return self._create(rhs)
        except:
            print path
            raise
    
    def _create(self, path):
        lhs = None
        try:
            lhs, rhs = path.split("/",1)
        except:
            pass

        if not lhs is None:
            rets = []
            for c in self.children:
                if c.partial_path == lhs or lhs =="*":
                    rets += c._create(rhs)
                    
            if len(rets)>0:
                return rets
            
            last_node = None
            first_node = None
            lst = path.split("/")
            print lst
            lst.reverse()
            for x in lst:
                if last_node is None:
                    nn = Node(x) 
                    first_node = nn
                else:
                    nn = Node(x, [last_node])
                    last_node.parent = nn
                last_node = nn

            last_node.parent = self
            self.children.append(last_node)
            return [first_node]
    
        nn = Node(path)
        nn.parent = self
        self.children.append(nn)
        return [nn]

    def __str__(self):
        if not self.parent is None:
            app = str(self.parent)
            if app.strip() == "": return self.partial_path
            return app +"::"+self.partial_path
        return self.partial_path

#c1= [Node("test1"), Node("test2"), Node("test3")]
#d = Node("",[Node("main",c1)])
#d.get_or_create("/main/*/test5")
# print [str(x) for x in d.get("/*/*/*")]
import sys
class DoxygenDocumentation:

    def __init__(self,files = []):
        self._compound_stack = []
        self.docs = Node("")
        self._current_compound= None
        self._loading_file = None
        for f in files:
#            print "Treating f", f
            self.load(f)


    def _get_text(self, subtree):
        val = ""
        for c in subtree.childNodes:
            if not c.nodeValue is None:
                val+= c.nodeValue
            else:
                val+= self._get_text(c)
        return val

    def scope_to_path(self, txt):
        np = "/"+txt.replace("::","/")
        co = {'<':0, '(': 0, '[': 0, '{':0}
        rc = {'>':'<', ')':'(', ']':'[', '}':'{'}
        i,j = 0, -1
        lasts = 0
        pointer = 0
        bp = 0
        todelete = []
        nstr = ""
        for s in np: 
            if s in co: 
                if lasts == 0: bp = i
                co[s]+=1
            if s in rc: 
                co[rc[s]]-=1
                ep = i
            ns = sum([k for k in co.itervalues()])
            if ns == 0 and lasts != 0:
                nstr+=np[pointer:bp]
                pointer = ep+1
            lasts=ns
            i+=1
        nstr+=np[pointer:]
#        print txt,"->", np, "->", nstr
        return nstr

    def _parse_enumvalue(self, subtree, path):
        newpath = None
        attributes = dict([(q, self._get_text(w)) for q,w in dict(subtree.attributes).iteritems()])
        for c in subtree.childNodes:
            name = c.nodeName.strip()
            val = self._get_text(c)
            attributes[name] = val
            if name =="name":
                newpath = path + "/"+ val

        nodes = self.docs.create(newpath)
        for n in nodes:
            n.attributes.update(attributes)

    def _template_param(self, child):
        attr = {"description": ""}
        ## Fixing parameters that has been 
        ## wrongly parsed by doxygen
        for c in child.childNodes:
            name = c.nodeName.strip()
            if "#" in name: continue
            val = self._get_text(c)
            
            co = {'<':0, '(': 0, '[': 0, '{':0}
            rc = {'>':'<', ')':'(', ']':'[', '}':'{'}
            i,j = 0, -1
            for s in val: 
                if s ==" " and sum([k for k in co.itervalues()]) == 0:                             
                    j = i
                if s in co: co[s]+=1
                if s in rc: co[rc[s]]-=1
                i+=1
            if j != -1:
                t,mem = val[0:j], val[j+1:]
                attr["type"] = t
                attr["declname"] = mem
                attr["defname"] = mem
            else:
                attr[name] = val
            
        return attr

    def _parse_template_params(self, subtree, node):
        lst = []
        for c in subtree.childNodes:
            name = c.nodeName.strip()
            val = self._get_text(c)
            if name =="param":
                lst.append(self._template_param(c))
        
        node.attributes['template_parameters'] += lst
        
    def _parse_memberdef(self, subtree):
        parse_children = False
        attributes = dict([(q, self._get_text(w)) for q,w in dict(subtree.attributes).iteritems()])
        attributes["parameters"] = []
        attributes['template_parameters'] = []
        attributes["is_type"] = ("typedef" == attributes["kind"])
        attributes["is_enum"] = ("enum" == attributes["kind"])
        attributes['is_member'] = True 
        attributes['is_namespace'] = False
        attributes['is_class'] = ("class" == attributes["kind"])
#        if attributes['id']=='classalps_1_1numeric_1_1matrix_1a33033173ca671a1c617c210a91dd2bea':
#            print "X", kind, attributes["kind"]


        path = None
        for c in subtree.childNodes:
            n2 = c.nodeName.strip()
            if n2.startswith("#"): continue
            txt = self._get_text(c).strip() 
            attributes[n2] = txt ## TODO: add support for references
            if n2 == "definition": 
                t = attributes["type"]

                co = {'<':0, '(': 0, '[': 0, '{':0}
                rc = {'>':'<', ')':'(', ']':'[', '}':'{'}
                i,j = 0, -1
                for s in txt: 
                    if s ==" " and sum([k for k in co.itervalues()]) == 0:                             
                        j = i
                    if s in co: co[s]+=1
                    if s in rc: co[rc[s]]-=1
                    i+=1
                if j == -1:
                    t, mem = "", txt
                else:
                    t,mem = txt[0:j], txt[j+1:]
#                    t, mem = txt.rsplit(" ",1) if " " in txt else ("", txt)
                if t == "": t = "void"
                path = self.scope_to_path(mem)
                attributes["fulltype"] = t
            elif n2=="location":
                fatt = dict([(q, self._get_text(w)) for q,w in dict(c.attributes).iteritems()])                
                attributes.update(fatt)
            elif n2=="param": ## TODO: add support for tparam
                add = {}
                for c2 in c.childNodes:
                    nn = c2.nodeName.strip()
                    val = self._get_text(c2) ## TODO: add support for references
                    add[nn] = val
                attributes["parameters"].append(add)
            elif n2 =="enumvalue":
                if path is None:
                    if "name" in attributes:
                        if not self._current_compound is None:
                            path = self._current_compound+"/"+attributes["name"]
                if not path is None:
                    self._parse_enumvalue(c,path)
                else:
                    raise BaseException("Could not determine path")

        if path is None:
            if "name" in attributes:
                if not self._current_compound is None:
                    path = self._current_compound+"/"+attributes["name"]
            else:
                raise BaseException("Variable with no name or path in %s"%self._loading_file)
#            print "Memberdef of ", path
        nodes = self.docs.create(path)
#            print [str(x) for x in nodes]
        for n in nodes:
            n.attributes.update(attributes)


    def _parse_compound_class(self, subtree, kind):
        name = subtree.nodeName.strip()
        if name == "compoundname":
            scope = self._get_text(subtree)
            path = self.scope_to_path(scope)
            node = self.docs.get_or_create(path)[0]
            node.attributes['is_member'] = False
            node.attributes['is_namespace'] = False
            node.attributes['is_class'] = (kind=="class")
            node.attributes['is_type'] = True
            node.attributes['doxygen_file'] = self._loading_file
            node.attributes['parameters'] = []
            node.attributes['template_parameters'] = []
            node.attributes["path"] = path            
            node.attributes["name"] = path.rsplit("/",1)[1] if "/" in path else path
            node.attributes["definition"] = "%s %s" % (kind, scope)

            self._current_compound = path
            self._compound_stack.append(node)

        elif name == "templateparamlist":
            self._parse_template_params(subtree, self._compound_stack[-1])
            n = self._compound_stack[-1]
            print n.attributes["path"]
            print [x for x in n.attributes["template_parameters"]]
            n.attributes["template_argstring"] = ", ".join([ "%s %s" % (x["type"],x["declname"]) for x in n.attributes["template_parameters"]])
            n.attributes["definition"] = "template< %s > %s" %(n.attributes["template_argstring"], n.attributes["definition"])

        elif name == "memberdef":
           self._parse_memberdef(subtree)
        else:
            for c in subtree.childNodes:
                self._parse_compound_class(c,kind)


    def _parse_compound(self,subtree):
        for c in subtree.childNodes:
            t = self._get_text(subtree.attributes["kind"])
            if t == "class":
                self._parse_compound_class(c,t)
            # TODO: add support for structs and files
        self._current_compound= None

    def _parse_tree(self, subtree):
        parse_children = True
        name = subtree.nodeName.strip()

        for c in subtree.childNodes:
            name = c.nodeName.strip()
            if name == "compounddef":
                self._parse_compound(c)
                self._compound_stack = self._compound_stack[:-1]
            else:
                self._parse_tree(c)


    def load(self, filename):
        self._loading_file = filename
        d = minidom.parse(filename)
        self._parse_tree(d)


    def get(self, path):
        return self.docs.get(path)


if __name__ == "__main__":
    import glob
    testfile = "/home/tfr/Documents/Alps/build/docs/doxygen/xml/classalps_1_1numeric_1_1matrix.xml"
    
    testfiles = glob.glob("/home/tfr/Documents/Alps/build/docs/doxygen/xml/*.xml")
    
#    d = DoxygenDocumentation(testfiles)
    d = DoxygenDocumentation([testfile])
    
    t = d.get("/alps/numeric/*")
    print "Len = ", len(t)
    print [str(x) for x in t]
    print "-"*100
    for x in t:
        print x.attributes
        print  str(x)
        if "is_member" in x.attributes and  x.attributes["is_member"]:
            print x.attributes["name"], "is",
            if "prot" in x.attributes: print x.attributes["prot"], 
            if "kind" in x.attributes: print x.attributes["kind"], 
            print "of type",
            if "fulltype" in x.attributes: print x.attributes["fulltype"],
            if "definition" in x.attributes: print "(%s)"%x.attributes["definition"],
            print
        else:
            print "Is not a member"
        print [str(q) for q in x.children]
        print "+++"
