from zope.app.testing import placelesssetup

from five.intid.site import add_intids
from plone.app.relations.utils import add_relations

from Products.Five import zcml

def setUp(app):
    placelesssetup.setUp()
    import Products.Five
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('permissions.zcml', Products.Five)
    zcml.load_config('configure.zcml', Products.Five)
    add_intids(app)
    add_relations(app)    
