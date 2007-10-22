from zope import interface
from zope import component
from zope.event import notify

from zope.app.container.contained import ObjectAddedEvent

from persistent import Persistent
from persistent.list import PersistentList

from plone.app.layout.composition.interfaces import *
from plone.app.relations.interfaces import IRelationshipSource

from Products.CMFCore.interfaces import ISiteRoot

class Composition(PersistentList):
    interface.implements(IComposition)
    
    def __init__(self, context):
        super(Composition, self).__init__()
        self.context = context
            
class Container(PersistentList):
    interface.implements(IContainer)
    
    def __init__(self, title=u"", description=u""):
        super(Container, self).__init__()
        self.title = title
        self.description = description
        
class Row(Container):
    interface.implements(IRow)

class Column(Container):
    interface.implements(IColumn)

class ContentTile(Persistent):
    interface.implements(IContentTile)

    __name__ = u""
    
    def __init__(self, obj=None):
        self.__parent__ = component.getUtility(ISiteRoot)
        self.view_method = u""

        notify(ObjectAddedEvent(self))

        if obj: self.target = obj

    def _get_target(self):
        source = IRelationshipSource(self)
        for target in source.getTargets():
            return target

    def _set_target(self, obj):
        source = IRelationshipSource(self)
        source.createRelationship(obj)

        # TODO: set a default view method
        self.view_method = u""

    target = property(_get_target, _set_target)
