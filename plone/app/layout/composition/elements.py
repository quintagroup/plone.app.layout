from zope import interface
from zope import component
from zope.event import notify

from zope.app.container.contained import ObjectAddedEvent

from persistent import Persistent
from persistent.list import PersistentList
from persistent.dict import PersistentDict

from StringIO import StringIO

from plone.app.layout.composition.interfaces import *
from plone.app.relations.interfaces import IRelationshipSource

from Products.CMFCore.interfaces import ISiteRoot

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

    __name__ = u""
    
    def __init__(self, obj=None):
        self.__parent__ = component.getUtility(ISiteRoot)
        
        notify(ObjectAddedEvent(self))
        if obj:
            self.setTarget(obj)
            
    def getTarget(self):
        source = IRelationshipSource(self)
        for target in source.getTargets():
            return target

    def setTarget(self, obj):
        source = IRelationshipSource(self)
        source.createRelationship(obj)

    def render(self, stream=None):
        target = self.getTarget()

        if target:
            output = target.title_or_id()
        else:
            output = u""

        if stream:
            stream.write(output)
        else:
            return output
