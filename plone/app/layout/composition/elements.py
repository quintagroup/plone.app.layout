from zope import interface

from persistent import Persistent
from persistent.list import PersistentList
from persistent.dict import PersistentDict

from StringIO import StringIO

from plone.app.layout.composition.interfaces import *

class Renderable:
    interface.implements(IRenderable)
    
    def render(self, stream=None):
        if stream:
            for item in self: item.render(stream)
        else:
            stream = StringIO()
            for item in self: item.render(stream)
            return stream.getvalue()

class Layout(PersistentList, Renderable):
    interface.implements(ILayout)

class Container(PersistentList, Renderable):
    interface.implements(IContainer)
    
    def __init__(self, title=u"", description=u""):
        super(Container, self).__init__()
        self.title = title
        self.description = description
        
class Row(Container):
    interface.implements(IRow)

class Column(Container):
    interface.implements(IColumn)

class Tile(Persistent):
    interface.implements(ITile)
    
    def __init__(self, obj):
        self.options = PersistentDict()

    def render(self, stream=None):
        output = u""

        if stream:
            stream.write(output)
        else:
            return output
