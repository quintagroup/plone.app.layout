from zope.i18nmessageid import MessageFactory
PloneMessageFactory = MessageFactory('plone')

from AccessControl import allow_module

# Make the navtree constructs available TTW
allow_module('plone.app.layout.navigation')
allow_module('plone.app.layout.navigation.root')
