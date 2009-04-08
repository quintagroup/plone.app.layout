from zope.i18n import translate
from zope.publisher.browser import BrowserView

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName


class DashboardView(BrowserView):
    """Power the dashboard
    """

    def actions(self):
        portal_actions = getToolByName(self.context, 'portal_actions')
        category = 'controlpanel/controlpanel_user'
        actions = portal_actions.listActionInfos(category=category)
        def _title(v):
            return translate(v.get('title'),
                             domain='plone',
                             context=self.request)
        actions.sort(key=_title)
        return actions

    @memoize
    def empty(self):
        return True
