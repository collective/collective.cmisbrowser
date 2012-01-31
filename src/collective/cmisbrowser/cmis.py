# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, aq_inner, aq_parent
from DateTime import DateTime
from Products.CMFDefault.permissions import View
from Products.CMFPlone import Batch
from Products.CMFCore.utils import getToolByName
from ZPublisher.BaseRequest import DefaultPublishTraverse

from Globals import InitializeClass

from collective.cmisbrowser.interfaces import CMISConnectorError
from collective.cmisbrowser.interfaces import ICMISStaleResult
from collective.cmisbrowser.interfaces import ICMISContent, ICMISFileResult
from collective.cmisbrowser.interfaces import ICMISDocument, ICMISFolder
from zope.interface import implements
from zope.datetime import time
from zope.app.component.hooks import getSite


def to_zope_datetime(datetime):
    return DateTime(*datetime.timetuple()[:6])


class CMISStaleResult(Implicit):
    """An unchanged file result from CMIS.
    """
    implements(ICMISStaleResult)
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self):
        pass

InitializeClass(CMISStaleResult)


class CMISFileResult(Implicit):
    """File content as download from CMIS.
    """
    implements(ICMISFileResult)
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self, filename, length, stream, mimetype):
        self.filename = filename
        self.length = length
        self.stream = stream
        self.mimetype = mimetype

InitializeClass(CMISFileResult)


class CMISContent(Implicit):
    """Refer a Document in a CMIS repositories.
    Follows the Plone API as much as possible.
    """
    implements(ICMISContent)
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)
    isPrincipiaFolderish = 0

    security.declarePublic('portal_type')
    portal_type = 'CMIS Document'
    portal_icon = '++resource++collective.cmisbrowser.document.png'

    def __init__(self, properties, connector):
        self._properties = properties
        self._connector = connector

    def refreshedBrowserDefault(self, request):
        return aq_inner(self), ('@@view',)

    def browserDefault(self, request):
        # Support for IF-MODIFIED-SINCE
        header = request.environ.get('HTTP_IF_MODIFIED_SINCE', None)
        if header is not None:
            header = header.split(';')[0]
            try:
                mod_since = long(time(header))
            except:
                mod_since = None
            else:
                last_mod = self.modified()
                if last_mod is not None:
                    last_mod = long(last_mod)
                    if last_mod > 0 and last_mod <= mod_since:
                        return CMISStaleResult().__of__(self), ('@@view',)
        return self.refreshedBrowserDefault(request)

    def publishTraverse(self, request, name):
        # Regular CMIS content are not traversable in CMIS.
        default = DefaultPublishTraverse(self, request)
        return default.publishTraverse(request, name)

    security.declareProtected(View, 'getId')
    def getId(self):
        path = self._properties.get('cmis:path')
        if path is not None:
            identifier = path.rsplit('/', -1)[-1].encode('utf-8')
            if identifier:
                return identifier
            # The root object must have an ID of None.
        return None

    security.declareProtected(View, 'getObject')
    def getObject(self):
        # Some view expect to have catalog brains
        return aq_inner(self)

    def CMISId(self):
        return self._properties['cmis:objectId']

    security.declareProtected(View, 'absolute_url')
    def absolute_url(self):
        url = aq_parent(aq_inner(self)).absolute_url()
        identifier = self.getId()
        if identifier is not None:
            url += '/' + identifier
        return url

    security.declareProtected(View, 'Title')
    def Title(self):
        return self._properties.get('cmis:name', u'CMIS Untitled Document')

    security.declareProtected(View, 'Description')
    def Description(self):
        return ''

    security.declareProtected(View, 'Creator')
    def Creator(self):
        return self._properties.get('cmis:createdBy')

    def created(self):
        return to_zope_datetime(self._properties.get('cmis:creationDate'))

    security.declareProtected(View, 'CreationDate')
    def CreationDate(self):
        return self.created().ISO()

    def modified(self):
        return to_zope_datetime(self._properties.get('cmis:lastModificationDate'))

    security.declareProtected(View, 'ModificationDate')
    def ModificationDate(self):
        return self.modified().ISO()

    def expires(self):
        return DateTime('2499/12/31')

    security.declareProtected(View, 'EffectiveDate')
    def EffectiveDate(self):
        return 'None'

    security.declareProtected(View, 'ExpirationDate')
    def ExpirationDate(self):
        return 'None'

    security.declareProtected(View, 'Format')
    def Format(self):
        return 'text/html'

    security.declareProtected(View, 'Subject')
    def Subject(self):
        return tuple()

    security.declareProtected(View, 'Type')
    def Type(self):
        return self.portal_type

    # Support for portal_type and portal_actions
    getPortalTypeName = Type

    def getTypeInfo(self):
        tool = getToolByName(getSite(), 'portal_types', None)
        if tool is not None:
            return tool.getTypeInfo(self.portal_type)
        return None


InitializeClass(CMISContent)



class CMISDocument(CMISContent):
    implements(ICMISDocument)
    security = ClassSecurityInfo()

    security.declarePublic('portal_type')
    portal_type = 'CMIS Document'
    portal_icon = '++resource++collective.cmisbrowser.document.png'

    def refreshedBrowserDefault(self, request):
        result = self._connector.get_object_content(aq_inner(self))
        return result.__of__(self), ('@@view',)

    def getId(self):
        identifier = self._properties.get('cmis:contentStreamFileName')
        if identifier is None:
            identifier = super(CMISDocument, self).getId()
        return identifier

    def Format(self):
        return self._properties.get('cmis:contentStreamFileName', 'text/html')


InitializeClass(CMISDocument)


class CMISFolder(CMISContent):
    implements(ICMISFolder)
    security = ClassSecurityInfo()
    isPrincipiaFolderish = 1

    security.declarePublic('portal_type')
    portal_type = 'CMIS Folder'
    portal_icon = '++resource++collective.cmisbrowser.folder.png'

    def publishTraverse(self, request, name):
        path = self._properties.get('cmis:path')
        if path:
            path = path.rstrip('/') + '/' + name
            content = self._connector.get_object_by_path(path)
            return content.__of__(aq_inner(self))
        return super(CMISFolder, self).publishTraverse(request, name)

    # This is used by Plone templates to list a folder content
    security.declareProtected(View, 'getFolderContents')
    def getFolderContents(self, *args, **kwargs):
        contents = map(
            lambda c: c.__of__(self),
            self._connector.get_object_children(self))
        if 'batch' in kwargs:
            return Batch(
                contents,
                kwargs.get('b_size', 100),
                int(self.REQUEST.get('b_start', 0)),
                orphan=0)
        return contents


InitializeClass(CMISFolder)


class CMISRootFolder(CMISFolder):

    def getId(self):
        # The root must have an id of None (as they are the root of the URL).
        return None


InitializeClass(CMISRootFolder)


CMIS_FACTORIES = {
    'cmis:folder': CMISFolder,
    'cmis:document': CMISDocument,
    'default': CMISContent}


def create_cmis_object(properties, connector, is_root=False):

    def get_factory():
        object_type = properties.get('cmis:objectTypeId')
        if object_type in CMIS_FACTORIES:
            return CMIS_FACTORIES[object_type]
        base_type = properties.get('cmis:baseTypeId')
        if base_type in CMIS_FACTORIES:
            return CMIS_FACTORIES[base_type]
        return CMIS_FACTORIES['default']

    factory = get_factory()
    if is_root:
        if not ICMISFolder.implementedBy(factory):
            raise CMISConnectorError('Connector root must be a folder.')
        # Upgrade factory to root folder.
        factory = CMISRootFolder
    return factory(properties, connector)
