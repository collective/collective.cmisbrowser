# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, aq_inner, aq_parent
from DateTime import DateTime
from Products.CMFDefault.permissions import View
from Products.CMFPlone import Batch
from ZPublisher.BaseRequest import DefaultPublishTraverse

from Globals import InitializeClass

from collective.cmisbrowser.interfaces import ICMISDocument, ICMISFolder
from zope.interface import implements


def to_zope_datetime(datetime):
    return DateTime(*datetime.timetuple()[:6])


class CMISDocument(Implicit):
    """Refer a Document in a CMIS repositories.
    Follows the Plone API as much as possible.
    """
    implements(ICMISDocument)
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)
    isPrincipiaFolderish = 0

    security.declarePublic('portal_type')
    portal_type = 'CMIS Document'
    portal_icon = '++resource++collective.cmisbrowser.document.png'

    def __init__(self, properties, connector):
        self._properties = properties
        self._connector = connector

    def getId(self):
        path = self._properties.get('cmis:path')
        if path is not None:
            identifier = path.rsplit('/', -1)[-1].encode('utf-8')
            if identifier:
                return identifier
            # The root object must have an ID of None.
            return None
        filename = self._properties.get('cmis:contentStreamFileName')
        if filename is not None:
            return filename
        return None

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

    security.declareProtected(View, 'Format')
    def Format(self):
        return self._properties.get('cmis:cmis:contentStreamFileName', 'text/html')

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

    security.declareProtected(View, 'Subject')
    def Subject(self):
        return tuple()

    security.declareProtected(View, 'Type')
    def Type(self):
        return self.portal_type


InitializeClass(CMISDocument)


class CMISFolder(CMISDocument):
    implements(ICMISFolder)
    security = ClassSecurityInfo()
    isPrincipiaFolderish = 1

    security.declarePublic('portal_type')
    portal_type = 'CMIS Folder'
    portal_icon = '++resource++collective.cmisbrowser.folder.png'

    def browserDefault(self, request):
        return aq_inner(self), ('@@view',)

    def publishTraverse(self, request, name):
        path = self._properties.get('cmis:path')
        if path:
            path = path.rstrip('/') + '/' + name
            content = self._connector.get_object_by_path(path)
            return content.__of__(aq_inner(self))
        default = DefaultPublishTraverse(self, request)
        return default.publishTraverse(request, name)

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



CMIS_FACTORIES = {
    'cmis:folder': CMISFolder,
    'cmis:document': CMISDocument,
    'default': CMISDocument}


def create_cmis_object(properties, connector):
    object_type = properties.get('cmis:objectTypeId')
    if object_type in CMIS_FACTORIES:
        return CMIS_FACTORIES[object_type](properties, connector)
    base_type = properties.get('cmis:baseTypeId')
    if base_type in CMIS_FACTORIES:
        return CMIS_FACTORIES[base_type](properties, connector)
    return CMIS_FACTORIES['default'](properties, connector)
