from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.viewlet.interfaces import IViewlet

from Products.CMFCore.utils import getToolByName

from plone.app.layout.utils import safe_unicode


class AnalyticsViewlet(BrowserView):
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        pass

    def render(self):
        """render the webstats snippet"""
        ptool = getToolByName(self.context, "portal_properties")
        snippet = safe_unicode(ptool.site_properties.webstats_js)
        return snippet
