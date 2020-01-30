"""
class for simple html file creation

author: Damien Lachouette
Date: 15/02/2017
mail: argawaen@argawaen.net
"""

# standard predifed color in html
__PREDEFINED_COLOR = { 
    'white' : '#FFFFFF',
    'silver': '#C0C0C0',
    'gray'  : '#808080',
    'black' : '#000000',
    'red'   : '#FF0000',
    'maroon': '#800000',
    'yellow': '#FFFF00',
    'olive' : '#808000',
    'lime'  : '#00FF00',
    'green' : '#008000',
    'aqua'  : '#00FFFF',
    'teal'  : '#008080',
    'blue'  : '#0000FF',
    'navy'  : '#000080',
    'fushia': '#FF00FF',
    'purple': '#800080'
    }
    

def iscolorstr(stri):
    '''
    test if the given string is representing a color
    '''
    if type(stri)!=str:
        return False
    if stri in __PREDEFINED_COLOR.keys():
        return True
    if not stri.startswith("#"):
        return False
    if len(stri)!=7:
        return False
    for i in range(1,6):
        if stri[i] not in ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']:
            return False
    return True

class htmlfile:
    '''
    class for handling simple html file
    '''
    def __init__(self, name="",title=""):
        '''
        '''
        # the file name
        if type(name)==str:
            self.__name=name
        # the title to use in html head
        if type(title)==str:
            self.__title=title
        # the body content
        self.__lines = []
        # list of keyword to be colored
        self.__keywordcolor = {}
        # if the text is formatted
        self.__formatted = False
    #
    #
    def setTitle(self,title=""):
        '''
        set the html head title
        '''
        if type(title)==str:
            self.__title=title
    #
    def setName(self,name=""):
        '''
        define the name of the file
        '''
        if type(name)==str:
            self.__name=name
    #
    def setFormatted(self,form=True):
        '''
        define if the text output should be formatted
        Formatted means multiline files with indentation
        unformatted means single line file without indentation (smaller file, compacted form)
        '''
        if type(form)==bool:
            self.__formatted = form
    #
    def setKeywordColor(self,key,color=None):
        '''
        add a keyword and a color to the actual list
        if key is a string, then color should be a color string
        if key is a list (of keys [==str] )color should be a list of color string with the same size
        if key is a dict, the its keys should be str and content should be color string
        '''
        # case of a string argument
        if type(key)==str:
            if type(color)!=str:
                return
            if iscolorstr(color):
                self.__keywordcolor[key]=color
            else:
                if color=="":
                    if key in self.__keywordcolor.keys():
                        self.__keywordcolor.pop(key)
        # case of a list argument
        if type(key)==list:
            if type(color)!=list:
                return
            if len(color)!=len(key):
                return
            for k in key:
                if type(k)!=str:
                    continue
                iid=key.index(k)
                if iscolorstr(color[iid]):
                    self.__keywordcolor[k]=color[iid]
        # case of a dictionnary argument
        if type(key)==dict:
            for k in key.keys():
                if type(k)!=str:
                    continue
                if iscolorstr(key[k]):
                    self.__keywordcolor[k]=key[k]
    #
    def clearKeyword(self):
        '''
        clear the keywords definition
        '''
        self.__keywordcolor.clear()
    #
    def clearContent(self):
        '''
        clear the content of the file (keep title, keyword)
        '''
        self.__lines.clear()
    #
    def clear(self):
        '''
        clear everything
        '''
        self.__title=""
        self.__lines.clear()
        self.__keywordcolor.clear()
    #
    def generate(self):
        '''
        generate the html code
        '''
        lend=""
        stab=""
        if self.__formatted: 
            lend="\n"
            stab="\t"
        out=""
        out+="<!DOCTYPE html>"+lend
        out+="<html>"+lend
        out+=stab+"<head>"+lend
        out+=stab+stab+"<meta charset=\"utf-8\" />"+lend
        if self.__title != "":
            out+=stab+stab+"<title>"+self.__title+"</title>"+lend
        out+=stab+"</head>"+lend
        out+=stab+"<body>"+lend
        for line in self.__lines:
            line=self.__applyKeywordColor(line)
            out+=stab+stab+line+lend
        out+=stab+"</body>"+lend
        out+="</html>"+lend
        return out
    #
    def writeFile(self):
        '''
        write the html code into the file
        '''
        if self.__name=="":
            return
        fo=open(self.__name,"w")
        fo.write(self.generate())
        fo.close()
    #
    def addLine(self,line,capsule=""):
        '''
        low level adding line
        '''
        if type(line)!=str:
            return
        laline=""
        if capsule!="":
            laline+="<"+capsule+">"
        laline+=line
        if capsule!="":
            laline+="</"+capsule+">"
        self.__lines.append(laline)
    #
    def addSection(self,title,level=1):
        '''
        shortcut for adding section title
        '''
        if type(title)!=str:
            return
        if level<1 or level>5 :
            return
        caps="h"+str(level)
        self.addLine(title,caps)
    #
    def addParargraph(self,content):
        '''
        shortcut for adding paragraph
        '''
        if type(content)!=str:
            return
        self.addLine(content,"p")
    #
    def addPreformatted(self,content):
        '''
        shortcut for adding preformatted text
        '''
        if type(content)!=str:
            return
        if content=="":
            return
        self.addLine("<pre>","")
        self.addLine(content,"")
        self.addLine("</pre>","")
    #
    def addList(self,title,items,number=False,niv=0):
        '''
        '''
        if type(title)!=str:
            return
        if type(niv)!=int:
            return
        if type(number)!=bool:
            return
        contents=[]
        if type(items)==str:
            contents=items.splitlines()
        elif type(items)==list:
            contents=items
        else:
            return
        if len(contents)==0:
            return
        pre=""
        tab=""
        if self.__formated:
            tab="\t"
            for i in range(niv):
                pre+="\t"
                i
        if number:
            self.addLine(pre+"<ol>"+title,"")
        else:
            self.addLine(pre+"<ul>"+title,"")
        for item in contents:
            if type(item)==str:
                self.addLine(pre+tab+"<li>"+item+"</li>","")
            elif type(item)==list:
                self.addList("",item,number,niv+1)
            elif type(item)==dict:
                t=""
                if "title" in item.keys():
                    t=item["title"]
                n=False
                if "number" in item.keys():
                    n=item["number"]
                it=[]
                if "items" in item.keys():
                    it=item["items"]
                self.addList(t,it,n,niv+1)
            else:
                continue
        if number:
            self.addLine(pre+"</ol>","")
        else:    
            self.addLine(pre+"</ul>","")
    #
    def __applyKeywordColor(self,line,case=True):
        '''
        private function that add the html anchor for text coloring according the the keyword list
        '''
        if type(line)!=str:
            return ""
        if type(case)!=bool:
            return ""
        if line=="":
            return ""
        oline=line
        for key in self.__keywordcolor.keys():
            if key in oline:
                str(oline).replace(key, +"<font color=\""+self.__keywordcolor[key]+">"+key+"</font>")
            if not case:
                if key.upper() in oline:
                    str(oline).replace(key.upper(), +"<font color=\""+self.__keywordcolor[key]+">"+key.upper()+"</font>")
                if key.lower() in oline:
                    str(oline).replace(key.lower(), +"<font color=\""+self.__keywordcolor[key]+">"+key.lower()+"</font>")
        return oline
    #
    #