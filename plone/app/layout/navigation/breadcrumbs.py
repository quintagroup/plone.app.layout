from plone.navigation.interfaces import IHideFromBreadcrumbs
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView

from Acquisition import aq_base
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName

from plone.app.layout.utils import pretty_title_or_id
from .defaultpage import isDefaultPage
from .interfaces import INavigationBreadcrumbs
from .root import getNavigationRoot


def get_url(item):
    if hasattr(aq_base(item), 'getURL'):
        # Looks like a brain
        return item.getURL()
    return item.absolute_url()

def get_id(item):
    getId = getattr(item, 'getId')
    if not callable(getId):
        # Looks like a brain
        return getId
    return getId()

def get_view_url(context):
    props = getToolByName(context, 'portal_properties')
    stp = props.site_properties
    view_action_types = stp.getProperty('typesUseViewActionInListings', ())

    item_url = get_url(context)
    name = get_id(context)

    if context.portal_type in view_action_types:
        item_url += '/view'
        name += '/view'

    return name, item_url


class CatalogNavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = self.context
        request = self.request
        ct = getToolByName(context, 'portal_catalog')
        query = {}

        # Check to see if the current page is a folder default view, if so
        # get breadcrumbs from the parent folder
        if isDefaultPage(aq_parent(context), context):
            currentPath = '/'.join(aq_parent(context).getPhysicalPath())
        else:
            currentPath = '/'.join(context.getPhysicalPath())
        query['path'] = {'query':currentPath, 'navtree':1, 'depth': 0}

        rawresult = ct(**query)

        # Sort items on path length
        dec_result = [(len(r.getPath()),r) for r in rawresult]
        dec_result.sort()

        rootPath = getNavigationRoot(context)

        # Build result dict
        result = []
        for r_tuple in dec_result:
            item = r_tuple[1]

            # Don't include it if it would be above the navigation root
            itemPath = item.getPath()
            if rootPath.startswith(itemPath):
                continue

            id, item_url = get_view_url(item)
            data = {'Title': pretty_title_or_id(context, item),
                    'absolute_url': item_url}
            result.append(data)
        return result


class PhysicalNavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = self.context
        request = self.request
        container = aq_parent(context)

        try:
            name, item_url = get_view_url(context)
        except AttributeError:
            print context
            raise

        if container is None:
            return ({'absolute_url': item_url,
                     'Title': pretty_title_or_id(context, context),
                    },)

        view = getMultiAdapter((container, request), name='breadcrumbs_view')
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        if base:
            item_url = '%s/%s' % (base[-1]['absolute_url'], name)

        rootPath = getNavigationRoot(context)
        itemPath = '/'.join(context.getPhysicalPath())

        # don't show default pages in breadcrumbs or pages above the navigation root
        if not isDefaultPage(container, context) and not rootPath.startswith(itemPath):
            base += ({'absolute_url': item_url,
                      'Title': pretty_title_or_id(context, context),
                     },)

        return base


class RootPhysicalNavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        # XXX Root never gets included, it's hardcoded as 'Home' in
        # the template. We will fix and remove the hardcoding and fix
        # the tests.
        return ()
