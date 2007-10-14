from zope.testing import doctest

from unittest import TestSuite

from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Products.CMFCore.utils import getToolByName

setupPloneSite()

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

from zope.component import provideAdapter

from plone.app.layout.composition.interfaces import IComposition
from plone.app.layout.composition import getComposition

from Products.ATContentTypes.content.folder import ATFolder

class LayoutCompositionTestCase(FunctionalTestCase):
    """base test case with convenience methods for all page composition tests."""

    def afterSetUp(self):
        super(LayoutCompositionTestCase, self).afterSetUp()

        # provide layout composition capabilities to ATFolder objects
        provideAdapter(getComposition, (ATFolder,), provides=IComposition)
        
    def getToolByName(self, name):
        """docstring for getToolByName"""
        return getToolByName(self.portal, name)

def test_suite():
    tests = ['README.txt']
    suite = TestSuite()
    for test in tests:
        suite.addTest(FunctionalDocFileSuite(test,
            optionflags=OPTIONFLAGS,
            package="plone.app.layout.composition",
            test_class=LayoutCompositionTestCase))
    return suite
