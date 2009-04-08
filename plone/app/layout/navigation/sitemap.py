from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implements
from zope.publisher.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils

from plone.app.layout.navigation.basenavtree import buildFolderTree
from plone.app.layout.navigation.basenavtree import NavtreeStrategyBase
from plone.app.layout.navigation.navtree import NavtreeQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import ISiteMap
from plone.app.layout.navigation.interfaces import ISitemapView
from plone.app.layout.navigation.root import getNavigationRoot


class SitemapView(BrowserView):
    implements(ISitemapView)

    def createSiteMap(self):
        context = self.context
        view = getMultiAdapter((context, self.request),
                               name='sitemap_builder_view')
        data = view.siteMap()
        properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        bottomLevel = navtree_properties.getProperty('bottomLevel', 0)
        # XXX: The recursion should probably be done in python code
        return context.portlet_navtree_macro(children=data.get('children',[]),
                                             level=1, bottomLevel=bottomLevel)

class SitemapQueryBuilder(NavtreeQueryBuilder):
    """Build a folder tree query suitable for a sitemap
    """

    def __init__(self, context):
        NavtreeQueryBuilder.__init__(self, context)
        portal_url = getToolByName(context, 'portal_url')
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        sitemapDepth = navtree_properties.getProperty('sitemapDepth', 2)
        self.query['path'] = {'query' : portal_url.getPortalPath(),
                              'depth' : sitemapDepth}

class SitemapNavtreeStrategy(NavtreeStrategyBase):
    """The navtree building strategy used by the sitemap, based on
    navtree_properties
    """
    implements(INavtreeStrategy)

    def __init__(self, context, view=None):
        self.context = context
        
        portal_url = getToolByName(context, 'portal_url')
        self.portal = portal_url.getPortalObject()
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        site_properties = getattr(portal_properties, 'site_properties')
        self.excludedIds = {}
        for id in navtree_properties.getProperty('idsNotToList', ()):
            self.excludedIds[id] = True
        self.parentTypesNQ = navtree_properties.getProperty('parentMetaTypesNotToQuery', ())
        self.viewActionTypes = site_properties.getProperty('typesUseViewActionInListings', ())

        self.showAllParents = navtree_properties.getProperty('showAllParents', True)
        self.rootPath = getNavigationRoot(context)

        membership = getToolByName(context, 'portal_membership')
        self.memberId = membership.getAuthenticatedMember().getId()

    def nodeFilter(self, node):
        item = node['item']
        if getattr(item, 'getId', None) in self.excludedIds:
            return False
        elif getattr(item, 'exclude_from_nav', False):
            return False
        else:
            return True

    def subtreeFilter(self, node):
        portalType = getattr(node['item'], 'portal_type', None)
        if portalType is not None and portalType in self.parentTypesNQ:
            return False
        else:
            return True

    def decoratorFactory(self, node):
        context = self.context
        request = context.REQUEST
        
        newNode = node.copy()
        item = node['item']

        portalType = getattr(item, 'portal_type', None)
        itemUrl = item.getURL()
        if portalType is not None and portalType in self.viewActionTypes:
            itemUrl += '/view'

        isFolderish = getattr(item, 'is_folderish', None)
        showChildren = False
        if isFolderish and (portalType is None or portalType not in self.parentTypesNQ):
            showChildren = True

        ploneview = getMultiAdapter((context, request), name=u'plone')

        newNode['Title'] = utils.pretty_title_or_id(context, item)
        newNode['absolute_url'] = itemUrl
        newNode['getURL'] = itemUrl
        newNode['path'] = item.getPath()
        newNode['item_icon'] = ploneview.getIcon(item)
        newNode['Creator'] = getattr(item, 'Creator', None)
        newNode['creation_date'] = getattr(item, 'CreationDate', None)
        newNode['portal_type'] = portalType
        newNode['review_state'] = getattr(item, 'review_state', None)
        newNode['Description'] = getattr(item, 'Description', None)
        newNode['show_children'] = showChildren
        newNode['no_display'] = False # We sort this out with the nodeFilter

        idnormalizer = queryUtility(IIDNormalizer)
        newNode['normalized_portal_type'] = idnormalizer.normalize(portalType)
        newNode['normalized_review_state'] = idnormalizer.normalize(newNode['review_state'])

        return newNode

    def showChildrenOf(self, object):
        getTypeInfo = getattr(object, 'getTypeInfo', None)
        if getTypeInfo is not None:
            portal_type = getTypeInfo().getId()
            if portal_type in self.parentTypesNQ:
                return False
        return True

class CatalogSiteMap(BrowserView):
    implements(ISiteMap)

    def siteMap(self):
        context = self.context

        queryBuilder = SitemapQueryBuilder(context)
        query = queryBuilder()

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context, query=query, strategy=strategy)
