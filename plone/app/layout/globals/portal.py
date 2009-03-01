from zope.interface import implements
from zope.publisher.browser import BrowserView
from plone.memoize.view import memoize_contextless

from Products.CMFCore.utils import getToolByName

from plone.app.layout.navigation.root import getNavigationRoot

from interfaces import IPortalState

class PortalState(BrowserView):
    """Information about the state of the portal
    """
    implements(IPortalState)

    @memoize_contextless
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @memoize_contextless
    def portal_title(self):
        return self.portal().Title()
        
    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()
        
    @memoize_contextless
    def navigation_root_path(self):
        return getNavigationRoot(self.context)
    
    @memoize_contextless
    def navigation_root_url(self):
        rootPath = self.navigation_root_path()
        return self.request.physicalPathToURL(rootPath)
    
    @memoize_contextless
    def default_language(self):
        site_properties = getToolByName(self.context, "portal_properties").site_properties
        return site_properties.getProperty('default_language', None)

    def language(self):
        return self.request.get('LANGUAGE', None) or \
                self.context.Language() or self.default_language()

    def locale(self):
        return self.request.locale

    @memoize_contextless
    def is_rtl(self):
        locale = self.request.locale
        if locale is None:
            # We cannot determine the orientation
            return False

        char_orient = locale.orientation.characters
        if char_orient == u'right-to-left':
            return True

        return False

    @memoize_contextless
    def member(self):
        tool = getToolByName(self.context, "portal_membership")
        return tool.getAuthenticatedMember()

    @memoize_contextless
    def anonymous(self):
        tool = getToolByName(self.context, "portal_membership")
        return bool(tool.isAnonymousUser())

    @memoize_contextless
    def friendly_types(self):
        context = self.context
        site_properties = getToolByName(context, "portal_properties").site_properties
        not_searched = site_properties.getProperty('types_not_searched', [])

        types = getToolByName(context, "portal_types").listContentTypes()
        return [t for t in types if t not in not_searched]
