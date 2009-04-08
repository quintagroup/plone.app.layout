from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from zope.component import getUtility
from zope.publisher.browser import BrowserView
from plone.memoize.view import memoize
from plone.navigation.interfaces import INonStructuralFolder

from Acquisition import aq_base, aq_parent
from DateTime import DateTime

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interface import IBrowserDefault
from Products.CMFPlone import utils

from interfaces import IContextState

BLACKLISTED_CATEGORIES = (
    'folder_buttons',
    'object_buttons',
    'controlpanel',
    'controlpanel_addons',
    'controlpanel_advanced',
    )


class ContextState(BrowserView):
    """Information about the state of the current context
    """
    
    implements(IContextState)
    
    @memoize
    def current_page_url(self):
        url = self.current_base_url()
        query = self.request.get('QUERY_STRING', None)
        if query:
            url += '?' + query
        return url
        
    @memoize
    def current_base_url(self):
        return self.request.get('ACTUAL_URL',
                 self.request.get('VIRTUAL_URL',
                   self.request.get('URL', 
                     self.context.absolute_url())))

    @memoize
    def canonical_object(self):
        context = self.context
        if self.is_default_page():
            return aq_parent(context)
        else:
            return context

    @memoize
    def canonical_object_url(self):
        return self.canonical_object().absolute_url()
            
    @memoize
    def view_url(self):
        """URL to use for viewing

        Files and Images get downloaded when they are directly
        called, instead of with /view appended.  We want to avoid that.
        """
        view_url = self.object_url()
        portal_properties = getToolByName(self.context, 'portal_properties', None)
        if portal_properties is not None:
            site_properties = getattr(portal_properties, 'site_properties', None)
            portal_type = getattr(aq_base(self.context), 'portal_type', None)
            if site_properties is not None and portal_type is not None:
                use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
                if portal_type in use_view_action:
                    view_url = view_url + '/view'
        return view_url

    @memoize
    def view_template_id(self):
        context = self.context

        if IBrowserDefault.providedBy(context):
            browserDefault = context
        else:
            browserDefault = queryAdapter(context, IBrowserDefault)

        if browserDefault is not None:
            try:
                return browserDefault.getLayout()
            except AttributeError:
                # Might happen if FTI didn't migrate yet.
                pass

        action = self._lookupTypeActionTemplate('object/view')
        if not action:
            action = self._lookupTypeActionTemplate('folder/folderlisting')

        return action

    @memoize
    def is_view_template(self):
        current_url = self.current_base_url()
        canonical_url = self.canonical_object_url()
        object_url = self.object_url()
        
        if current_url.endswith('/'):
            current_url = current_url[:-1]
        
        if current_url == canonical_url or current_url == object_url:
            return True
        elif current_url == object_url + '/view':
            return True
        
        template_id = self.view_template_id()
        if current_url == "%s/%s" % (object_url, template_id):
            return True
        elif current_url == "%s/@@%s" % (object_url, template_id):
            return True
        
        return False

    @memoize
    def object_url(self):
        return self.context.absolute_url()

    @memoize
    def object_title(self):
        context = self.context
        return utils.pretty_title_or_id(context, context)

    @memoize
    def workflow_state(self):
        tool = getToolByName(self.context, "portal_workflow")
        return tool.getInfoFor(self.context, 'review_state', None)

    def parent(self):
        return aq_parent(self.context)

    @memoize
    def folder(self):
        context = self.context
        if self.is_structural_folder() and not self.is_default_page():
            return context
        else:
            return aq_parent(context)

    @memoize
    def is_expired(self, content=None):
        if content is None:
            content = self.context
        expiry = None

        # ExpirationDate should have an ISO date string, which we need to
        # convert to a DateTime

        # Try DC accessor first
        if getattr(aq_base(content), 'ExpirationDate', None) is not None:
            expiry = content.ExpirationDate

        # Try the direct way
        if (not expiry and
            getattr(aq_base(content), 'expires', None) is not None):
            expiry = content.expires

        # See if we have a callable
        if callable(expiry):
            expiry = expiry()

        # Convert to DateTime if necessary, ExpirationDate may return 'None'
        if expiry and expiry != 'None' and isinstance(expiry, basestring):
            expiry = DateTime(expiry)

        if isinstance(expiry, DateTime) and expiry.isPast():
            return True
        return False

    @memoize
    def is_folderish(self):
        return bool(getattr(aq_base(self.context), 'isPrincipiaFolderish', False))
            
    @memoize
    def is_structural_folder(self):
        folderish = self.is_folderish()
        if not folderish:
            return False
        elif INonStructuralFolder.providedBy(self.context):
            return False
        else:
            return folderish
        
    @memoize
    def is_default_page(self):
        context = self.context
        container = aq_parent(context)
        if not container:
            return False
        view = getMultiAdapter((container, self.request), name='default_page')
        return view.isDefaultPage(context)
    
    @memoize
    def is_portal_root(self):
        context = self.context
        portal = getUtility(ISiteRoot)
        return aq_base(context) is aq_base(portal) or \
            (self.is_default_page() and
             aq_base(aq_parent(context)) is aq_base(portal))
    
    @memoize
    def is_editable(self):
        tool = getToolByName(self.context, "portal_membership")
        return bool(tool.checkPermission('Modify portal content', self.context))
    
    @memoize
    def is_locked(self):
        # plone_lock_info is registered on marker interface ITTWLockable, since
        # not everything may want to parttake in its lock-stealing ways.
        lock_info = queryMultiAdapter((self.context, self.request), name='plone_lock_info')
        if lock_info is not None:
            return lock_info.is_locked_for_current_user()
        else:
            context = self.context
            lockable = getattr(context.aq_explicit, 'wl_isLocked', None) is not None
            return lockable and context.wl_isLocked()

    @memoize
    def actions(self, category, max=-1):
        context = self.context
        tool = getToolByName(context, "portal_actions")
        return tool.listActionInfos(
            object=context,
            category=category,
            max=max,
            )

    # Helper methods
    def _lookupTypeActionTemplate(self, actionId):
        context = self.context
        fti = context.getTypeInfo()
        try:
            # XXX: This isn't quite right since it assumes the action starts with ${object_url}
            action = fti.getActionInfo(actionId)['url'].split('/')[-1]
        except ValueError:
            # If the action doesn't exist, stop
            return None

        # Try resolving method aliases because we need a real template_id here
        action = fti.queryMethodID(action, default = action, context = context)

        # Strip off leading /
        if action and action[0] == '/':
            action = action[1:]
        return action
