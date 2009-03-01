from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.layout.viewlets import ViewletBase


class StatusMessageViewlet(ViewletBase):

    render = ViewPageTemplateFile('status.pt')

    def messages(self):
        return IStatusMessage(self.request).showStatusMessages()
