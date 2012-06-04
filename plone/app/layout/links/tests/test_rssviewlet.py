from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.app.layout.links.viewlets import RSSViewlet
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFCore.utils import getToolByName


class TestRSSViewletView(ViewletsTestCase):
    """
    Test the document by line viewlet
    """

    def afterSetUp(self):
        pass

    def test_RSSViewlet(self):
        settings = IFeedSettings(self.portal)
        if settings.enabled:
            # make sure syndication is disabled
            self.loginAsPortalOwner()
            settings.enabled = False
            self.logout()
        request = self.app.REQUEST
        viewlet = RSSViewlet(self.portal, request, None, None)
        viewlet.update()
        result = viewlet.render()
        self.assertEquals(result.strip(), '')
        self.loginAsPortalOwner()
        settings.enabled = True
        self.logout()
        request = self.app.REQUEST
        viewlet = RSSViewlet(self.portal, request, None, None)
        viewlet.update()
        result = viewlet.render()
        self.failIf("<link" not in result)
        self.failIf("http://nohost/plone/RSS" not in result)


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
