from elements import Layout

from zope.interface import implements
from zope.app.annotation.interfaces import IAnnotations

KEY = 'plone.app.layout.composition'

def getComposition(context):
    annotations = IAnnotations(context)

    composition = annotations.get(KEY)
    if composition is None:
        composition = annotations[KEY] = Composition(context)

    return composition

class Composition(object):
    def __init__(self, context):
        self.context = context
        self.layout = Layout()
        
    def render(self):
        return self.layout.render()
