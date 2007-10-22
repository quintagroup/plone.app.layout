Composition package
===================

This package adds layout composition capabilities to content objects.

Compositions are rendered by a special view that tries to adapt the container
to the IComposition interface.

  >>> from plone.app.layout.composition.interfaces import IComposition
  >>> composition = IComposition(folder)

Compositions are persistent objects:

  >>> from persistent.interfaces import IPersistent
  >>> IPersistent.providedBy(composition)
  True

Setup
-----

We rely on the BeautifulSoup library to make HTML-snippets readable.

  >>> from BeautifulSoup import BeautifulSoup as Soup

First we need to set up the relations machinery:

  >>> from five.intid.site import add_intids
  >>> from plone.app.relations.utils import add_relations
  >>> add_intids(portal); add_relations(portal)    
  
Data model
----------

The data model is based on rows and columns; while columns can be added only
to rows, rows can be added to both columns as well as the main container.
Content objects are added as relations using content proxies.

Let's add a simple layout. The layout elements are defined in the `elements`
module.

  >>> from plone.app.layout.composition import elements

Elements are instantiated using simple constructors:
  
  >>> row = elements.Row(u"Some row")
  >>> column = elements.Column(u"Some column")

Let's add a new document and make a tile out of it:

  >>> _ = folder.invokeFactory(id=u"document", type_name='Document')
  >>> document = folder[_]
  >>> tile = elements.ContentTile(document)
  
We can use the standard list api to add elements:

  >>> column.append(tile)
  >>> row.append(column)
  >>> composition.append(row)

Render model
------------

  >>> from plone.app.layout.composition.tests import TestRequest
  >>> request = TestRequest('en')

  >>> from Products.Five.browser import BrowserView
  >>> view = BrowserView(document, request)

  >>> from zope.component import getMultiAdapter
  >>> from zope.contentprovider.interfaces import IContentProvider

  >>> provider = getMultiAdapter((composition, request, view),
  ...                            IContentProvider)

  >>> provider.update()
  >>> print Soup(provider.render()).prettify()
  <div class="composition">
   <div class="row">
    <div class="column">
     <h2>
      document
     </h2>
    </div>
   </div>
  </div>
  <BLANKLINE>

Rendering content tiles
-----------------------

To render the composition we need to provide `tile views` for the content
objects.

Let's register a simple document tile.

  >>> from zope import interface, component
  >>> from zope.viewlet.interfaces import IViewlet

  >>> class DocumentViewlet(BrowserView):
  ...     interface.implements(IViewlet)
  ...
  ...     def __init__(self, context, request, view, manager):
  ...         self.__parent__ = view
  ...         self.context = context
  ...
  ...     def update(self):
  ...         pass
  ...
  ...     def render(self):
  ...         return u'<div class="document">%s</div>' % self.context.title_or_id()

  >>> from plone.app.layout.composition.interfaces import IColumn
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer 
  >>> from zope.publisher.interfaces.browser import IBrowserView
  >>> from Products.ATContentTypes.interfaces import IATDocument

  >>> component.provideAdapter(
  ...     DocumentViewlet,
  ...     (interface.Interface, IDefaultBrowserLayer, IBrowserView, IColumn),
  ...     IViewlet, name=u'my_document_viewlet')

Let's set make this viewlet the view method for our document and render the composition
again.

  >>> tile.view_method = u'my_document_viewlet'
  >>> provider.update()
  >>> print Soup(provider.render()).prettify()
  <div class="composition">
   <div class="row">
    <div class="column">
     <div class="document">
      document
     </div>
    </div>
   </div>
  </div>
  <BLANKLINE>
