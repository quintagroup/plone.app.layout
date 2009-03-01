from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView
from plone.app.layout.viewlets import ViewletBase
from plone.navigation.interfaces import INextPreviousProvider

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Acquisition import aq_parent


class NextPreviousView(BrowserView):
    """Information about next/previous navigation
    """

    def next(self):
        provider = self._provider()
        if provider is None:
            return None
        return provider.getNextItem(self.context)
    
    def previous(self):
        provider = self._provider()
        if provider is None:
            return None
        return provider.getPreviousItem(self.context)

    def enabled(self):
        provider = self._provider()
        if provider is None:
            return False
        return provider.enabled

    def _provider(self):
        # Note - the next/previous provider is the container of this object!
        # This may not support next/previous navigation, so code defensively
        return INextPreviousProvider(aq_parent(self.context), None)

    def isViewTemplate(self):
        plone = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        return plone.is_view_template()


class NextPreviousViewlet(ViewletBase, NextPreviousView):
    render = ZopeTwoPageTemplateFile('nextprevious.pt')


class NextPreviousLinksViewlet(ViewletBase, NextPreviousView):
    render = ZopeTwoPageTemplateFile('links.pt')
