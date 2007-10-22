from zope import interface, component

from zope.viewlet.manager import ViewletManagerBase
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager

from zope.contentprovider.interfaces import IContentProvider

from plone.app.layout.composition.interfaces import IComposition
from plone.app.layout.composition.interfaces import IRow
from plone.app.layout.composition.interfaces import IColumn

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class CompositionContentProvider(object):
    interface.implements(IComposition)
    template = ViewPageTemplateFile("templates/composition.pt")

    def __init__(self, context, request, view):
        self.__updated = False
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        providers = [component.getMultiAdapter((item, self.request, self.__parent__),
                                               IContentProvider) for item in self.context]

        for provider in providers:
            provider.update()
            
        self.providers = providers
        self.__updated = True

    def render(self):
        return self.template(providers=self.providers)
            
class RowContentProvider(CompositionContentProvider):
    interface.implements(IRow)
    template = ViewPageTemplateFile("templates/row.pt")

class ColumnContentProvider(CompositionContentProvider):
    interface.implements(IColumn)
    template = ViewPageTemplateFile("templates/column.pt")
    
    def update(self):
        self.viewlets = []

        for tile in self.context:
            target = tile.target

            if target:
                method = tile.view_method

                try:
                    viewlet = component.getMultiAdapter(
                        (target, self.request, self.__parent__, self),
                        IViewlet, name=method)
                except:
                    # fallback to default method
                    viewlet = component.getMultiAdapter(
                        (target, self.request, self.__parent__, self),
                        IViewlet, name=u"")
                                        
                self.viewlets.append(viewlet)
                    
        # update all viewlets
        [viewlet.update() for viewlet in self.viewlets]
        
    def filter(self, viewlets):
        return viewlets

    def sort(self, viewlets):
        return viewlets

    def render(self):
        return self.template(viewlets=self.viewlets)
