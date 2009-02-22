import zope.deferredimport

zope.deferredimport.deprecated(
    "It has been moved to plone.navigation.interfaces. " 
    "This alias will be removed in Plone 5.0",
    INextPreviousProvider = 'plone.navigation.interfaces:INextPreviousProvider',
    )
