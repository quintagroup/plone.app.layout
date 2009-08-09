from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import ViewletBase


CEILING_DATE = DateTime(2500, 0)
FLOOR_DATE = DateTime(1970, 0)

# dublic core accessor name -> metadata name
METADATA_DCNAME = {
    # The first two rows are handle in a special way
    # 'Description'      : 'description',
    # 'Subject'          : 'keywords',
    'Description'      : 'DC.description',
    'Subject'          : 'DC.subject',
    'Creator'          : 'DC.creator',
    'Contributors'     : 'DC.contributors',
    'Publisher'        : 'DC.publisher',
    'CreationDate'     : 'DC.date.created',
    'ModificationDate' : 'DC.date.modified',
    'Type'             : 'DC.type',
    'Format'           : 'DC.format',
    'Language'         : 'DC.language',
    'Rights'           : 'DC.rights',
    }


class DCKeywordViewlet(ViewletBase):
    index = ViewPageTemplateFile('dckeywords.pt')

    def listMetaTags(self):
        """Lists meta tags helper.

        Creates a mapping of meta tags -> values for the listMetaTags script.
        """
        result = {}
        context = self.context
        site_props = getToolByName(context, 'portal_properties').site_properties
        use_all = site_props.getProperty('exposeDCMetaTags', None)

        # Optimize for the common case
        if not use_all:
            description = context.Description()
            if description:
                return [('description', description)]
            else:
                return ()

        for accessor, key in METADATA_DCNAME.items():
            method = getattr(aq_inner(context).aq_explicit, accessor, None)
            if not callable(method):
                continue

            # Catch AttributeErrors raised by some AT applications
            try:
                value = method()
            except AttributeError:
                value = None

            if not value:
                # No data
                continue
            if accessor == 'Publisher' and value == 'No publisher':
                # No publisher is hardcoded
                continue
            if isinstance(value, (list, tuple)):
                # convert a list to a string
                value = ', '.join(value)

            # Special cases
            if accessor == 'Description':
                result['description'] = value
            elif accessor == 'Subject':
                result['keywords'] = value

            if use_all:
                result[key] = value

        if use_all:
            created = context.CreationDate()

            try:
                effective = context.EffectiveDate()
                if effective == 'None':
                    effective = None
                if effective:
                    effective = DateTime(effective)
            except AttributeError:
                effective = None

            try:
                expires = context.ExpirationDate()
                if expires == 'None':
                    expires = None
                if expires:
                    expires = DateTime(expires)
            except AttributeError:
                expires = None

            # Filter out DWIMish artifacts on effective / expiration dates
            if effective is not None and \
               effective > FLOOR_DATE and \
               effective != created:
                eff_str = effective.Date()
            else:
                eff_str = ''

            if expires is not None and expires < CEILING_DATE:
                exp_str = expires.Date()
            else:
                exp_str = ''

            if eff_str or exp_str:
                result['DC.date.valid_range'] = '%s - %s' % (eff_str, exp_str)

        return result.items()
