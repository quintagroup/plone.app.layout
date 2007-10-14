from zope.interface import Interface
from zope import schema

from Products.CMFPlone import PloneMessageFactory as _

class IRenderable(Interface):
    def render():
        """Renders the object in some format."""

class IContainer(IRenderable):
    """This interface is the base class for the layout elements
    promising a title and a description. Containers also provide
    rendering capabilities."""
    
    title = schema.TextLine(title=_(u"Title"))
    description = schema.TextLine(title=_(u"Description"))

class IComposition(IRenderable):
    """A composition object holds a layout and a means to render that
    layout."""
        
    layout = []

class ILayout(Interface):
    pass

class IRow(IContainer):
    pass

class IColumn(IContainer):
    pass

class IContentProxy(Interface):
    """Acts as a proxy for a relation to an existing content object.
    The `options` property holds information on how to render the
    target object."""
    
    options = {}
