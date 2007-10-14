from zope.interface import Interface
from zope import schema

from Products.CMFPlone import PloneMessageFactory as _

class IRenderable(Interface):
    def render(stream=None):
        """Renders the object in some format. Outputs to `stream` if
        applicable."""

class IContainer(IRenderable):
    """This interface is the base class for the layout elements
    promising a title and a description. Containers also provide
    rendering capabilities."""
    
    title = schema.TextLine(title=_(u"Title"))
    description = schema.TextLine(title=_(u"Description"))

class IComposition(IRenderable):
    """A composition object holds a layout and a means to render that
    layout."""
        
    layout = schema.List(title=_(u"Layout items"))

class ILayout(Interface):
    pass

class IRow(IContainer):
    pass

class IColumn(IContainer):
    pass

class ITile(Interface):
    """A tile is an object that holds content rendering information."""
    
    options = schema.Dict(title=_(u"Content rendering information"))
