Composition package
===================

This package adds layout composition capabilities to content objects.

Compositions are rendered by a special view that tries to adapt the container
to the IComposition interface.

  >>> from plone.app.layout.composition.interfaces import IComposition
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
  >>> tile = elements.Tile(portal['front-page'])

We use the standard list interface to add elements:

  >>> column.append(tile)
  >>> row.append(column)
  >>> layout.append(row)

Rendering
---------

We can render the entire composition or individual elements:

  >>> composition.render()
  u''
  >>> row.render()
  u''
  >>> column.render()
  u''
  >>> tile.render()
  u''
