Composition package
===================

This package adds layout composition capabilities to structural containers,
e.g. folders.

Compositions are rendered by a special view that tries to adapt the container
to the IComposition interface.

  >>> composition = IComposition(folder)
  
Data model
----------

The data model is based on rows and columns; while columns can be added only
to rows, rows can be added to both columns as well as the main container.
Content objects are added as relations using content proxies.

The data model is stored as a `layout` on the composition:

  >>> layout = composition.layout

Let's add a simple layout. The layout elements are defined in the `elements`
module.

  >>> from plone.app.layout.composition import elements

Elements are instantiated using simple constructors:
  
  >>> row = elements.Row(u"Some row")
  >>> column = elements.Column(u"Some column")
  >>> proxy = elements.ContentProxy(portal['front-page'])

We use the standard list interface to add elements:

  >>> column += proxy
  >>> row += column
  >>> layout += row

Rendering
---------

We can render the entire composition or individual elements:

  >>> composition.render()
  >>> row.render()
  >>> column.render()
  >>> proxy.render()
