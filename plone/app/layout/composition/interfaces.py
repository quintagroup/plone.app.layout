from zope.interface import Interface
from zope import schema

from zope.contentprovider.interfaces import IContentProvider
from zope.viewlet.interfaces import IViewletManager

from persistent.interfaces import IPersistent

from Products.CMFPlone import PloneMessageFactory as _

class IComposition(IPersistent, IContentProvider):
    """Base container for a composition."""
    
class IContainer(IPersistent, IContentProvider):
    """This interface is the base class for the layout elements
    promising a title and a description."""
    
    title = schema.TextLine(title=_(u"Title"))
    description = schema.TextLine(title=_(u"Description"))

class IRow(IContainer):
    pass

class IColumn(IContainer, IViewletManager):
    pass

class IPersistentTile(IPersistent):
    """A persistent tile is the most basic element in a page composition,
    promising persistency and rendering capabilities.""" 

class IContentTile(IPersistentTile):
    """A content tile is a persistent tile that provides an option to
    select the view method used for rendering."""

    view_method = schema.Choice(title=_(u"View method"),
                                vocabulary="plone.app.layout.composition.vocabularies.ViewMethodVocabulary")

    def render(request, view):
        pass
