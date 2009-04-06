from zope.component import getMultiAdapter
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import ViewletBase

from Products.CMFCore.utils import getToolByName


class FaviconViewlet(ViewletBase):

    render = ViewPageTemplateFile('favicon.pt')


class SearchViewlet(ViewletBase):

    render = ViewPageTemplateFile('search.pt')


class AuthorViewlet(ViewletBase):

    _template = ViewPageTemplateFile('author.pt')

    def update(self):
        super(AuthorViewlet, self).update()
        self.tools = getMultiAdapter((self.context, self.request),
                                     name='plone_tools')

    def show(self):
        properties = self.tools.properties()
        site_properties = getattr(properties, 'site_properties')
        anonymous = self.portal_state.anonymous()
        allowAnonymousViewAbout = site_properties.getProperty('allowAnonymousViewAbout', True)
        return not anonymous or allowAnonymousViewAbout

    def render(self):
        if self.show():
            return self._template()
        return u''


class NavigationViewlet(ViewletBase):

    render = ViewPageTemplateFile('navigation.pt')


class RSSViewlet(ViewletBase):
    def update(self):
        super(RSSViewlet, self).update()
        syntool = getToolByName(self.context, 'portal_syndication')
        if syntool.isSyndicationAllowed(self.context):
            self.allowed = True
            context_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_context_state')
            self.url = '%s/RSS' % context_state.object_url()
        else:
            self.allowed = False

    render = ViewPageTemplateFile('rsslink.pt')
