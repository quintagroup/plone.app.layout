from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils

from plone.app.layout.navigation.basenavtree import buildFolderTree
from plone.app.layout.navigation.basenavtree import NavtreeQueryBuilder
from plone.app.layout.navigation.interfaces import INavigationTree
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.sitemap import SitemapNavtreeStrategy
from plone.app.layout.navigation.root import getNavigationRoot


class DefaultNavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the default navigation portlet
    """
    implements(INavtreeStrategy)

    def __init__(self, context, view=None):
        SitemapNavtreeStrategy.__init__(self, context, view)
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        # XXX: We can't do this with a 'depth' query to EPI...
        self.bottomLevel = navtree_properties.getProperty('bottomLevel', 0)
        if view is not None:
            self.rootPath = view.navigationTreeRootPath()
        else:
            self.rootPath = getNavigationRoot(context)

    def subtreeFilter(self, node):
        sitemapDecision = SitemapNavtreeStrategy.subtreeFilter(self, node)
        if sitemapDecision == False:
            return False
        depth = node.get('depth', 0)
        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        else:
            return True

class CatalogNavigationTree(BrowserView):
    implements(INavigationTree)

    def navigationTreeRootPath(self):
        context = self.context

        portal_properties = getToolByName(context, 'portal_properties')
        portal_url = getToolByName(context, 'portal_url')

        navtree_properties = getattr(portal_properties, 'navtree_properties')

        currentFolderOnlyInNavtree = navtree_properties.getProperty('currentFolderOnlyInNavtree', False)
        if currentFolderOnlyInNavtree:
            if context.is_folderish():
                return '/'.join(context.getPhysicalPath())
            else:
                return '/'.join(utils.parent(context).getPhysicalPath())

        rootPath = getNavigationRoot(context)

        # Adjust for topLevel
        topLevel = navtree_properties.getProperty('topLevel', None)
        if topLevel is not None and topLevel > 0:
            contextPath = '/'.join(context.getPhysicalPath())
            if not contextPath.startswith(rootPath):
                return None
            contextSubPathElements = contextPath[len(rootPath)+1:].split('/')
            if len(contextSubPathElements) < topLevel:
                return None
            rootPath = rootPath + '/' + '/'.join(contextSubPathElements[:topLevel])

        return rootPath

    def navigationTree(self):
        context = self.context

        queryBuilder = NavtreeQueryBuilder(context)
        query = queryBuilder()

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context, query=query, strategy=strategy)
