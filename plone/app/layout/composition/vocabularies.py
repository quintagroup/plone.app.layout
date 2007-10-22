from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements

class ViewMethodVocabulary(object):
    """Vocabulary factory for an objects view methods."""

    implements(IVocabularyFactory)

    def __call__(self, context):
        # TODO: Not yet implemented
        return SimpleVocabulary([])
        
ViewMethodVocabulary = ViewMethodVocabulary()
