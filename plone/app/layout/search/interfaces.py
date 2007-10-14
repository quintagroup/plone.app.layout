from zope.interface import Interface

class ISearchView(Interface):
    def groupedSearch(local=False):
        """Return search results grouped by content type.

        The possible parameters are:

          term -- the search term

          local -- root the search at the current context
        """
