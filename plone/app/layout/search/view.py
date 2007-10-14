from zope.interface import implements
from zope.component import getUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory
from plone.app.layout.search.utils import quoteQuery
from plone.app.layout.search.interfaces import ISearchView
from plone.app.layout.navigation.root import getNavigationRoot
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class SearchView(BrowserView):
    implements(ISearchView)

    def typesWithViewAction(self):
        pp=getToolByName(self.context, "portal_properties")
        return pp.site_properties.getProperty("typesUseViewActionInListings", [])


    def getTypes(self):
        tt=getToolByName(self.context, "portal_types")

        factory=getUtility(IVocabularyFactory,
                name="plone.app.vocabularies.ReallyUserFriendlyTypes")

        typefilter=self.request.form.get("types", [])

        types=[]

        for v in factory(self.context):
            if typefilter and v.value not in typefilter:
                continue

            if v.title:
                title = translate(v.title, context=self.request)
            else:
                title = translate(v.token, domain='plone', context=self.request)

            info=tt.getTypeInfo(v.value)

            types.append(dict(id=v.value, title=title, icon=info.getIcon()))

        return types


    def hasSearchQuery(self):
        return bool(self.request.form.get("term", "").strip())


    @property
    def term(self):
        return self.request.form.get("term")


    @property 
    def local(self):
        return self.request.form.get("local", False)


    def baseQuery(self):
        query=dict(SearchableText=quoteQuery(self.term))
        if self.local:
            query["path"]=getNavigationRoot(self.context)

        return query


    def groupedSearch(self):
        ct=getToolByName(self.context, "portal_catalog")
        types=self.getTypes()

        query=self.baseQuery()

        viewtypes=self.typesWithViewAction()
        results=[]
        for typeinfo in types:
            result=dict(
                    id=typeinfo["id"],
                    title=typeinfo["title"],
                    icon=typeinfo["icon"],
                    )

            query["portal_type"]=typeinfo["id"]

            def morph(brain):
                info=dict(
                        title=brain.Title,
                        description=brain.Description,
                        url=brain.getURL(),
                        score=brain.data_record_normalized_score_,
                        )
                if brain.Type in viewtypes:
                    info["url"]+="/view"
                return info

            brains=ct.search(query)

            result["results"]=[morph(brain) for brain in brains[:5]]
            result["count"]=len(brains)

            if result["results"]:
                results.append(result)

        return results


class LiveSearchView(SearchView):
    def baseQuery(self):
        query=SearchView.baseQuery(self)
        query["SearchableText"]+="*"
        return query

