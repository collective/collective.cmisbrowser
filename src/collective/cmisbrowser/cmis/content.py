# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, aq_inner, aq_parent
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.permissions import View
from Products.CMFPlone.PloneBatch import Batch
from ZPublisher.BaseRequest import DefaultPublishTraverse

try:
    # Support Zope 2.12+
    from App.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass

from collective.cmisbrowser.interfaces import ICMISContent
from collective.cmisbrowser.interfaces import ICMISDocument, ICMISFolder
from collective.cmisbrowser.errors import CMISConnectorError
from collective.cmisbrowser.errors import CMISErrorTraverser
from collective.cmisbrowser.cmis.result import CMISStaleResult
from zope.interface import implements
from zope.datetime import time
from zope.app.component.hooks import getSite


def to_zope_datetime(datetime):
    return DateTime(*datetime.timetuple()[:6])

default_zone = DateTime().timezone()
logger = logging.getLogger('collective.cmisbrowser')


class CMISContent(Implicit):
    """Refer a Document in a CMIS repositories.
    Follows the Plone API as much as possible.
    """
    implements(ICMISContent)
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)
    isPrincipiaFolderish = 0
    # Make sure to disable comments
    allow_discussion = False

    security.declarePublic('portal_type')
    portal_type = 'CMIS Document'
    portal_icon = '++resource++collective.cmisbrowser.document.png'

    # We could get the browser using Acquiition, but that doesn't work
    # in properties.
    def __init__(self, properties, api):
        self._properties = properties
        self._api = api

    def refreshedBrowserDefault(self, request):
        return aq_inner(self), ('@@view',)

    def browserDefault(self, request=None):
        # Plone calls browserDefault without the correct information.
        if request is None:
            request = self.REQUEST

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

    security.declareProtected(View, 'absolute_url')
    def absolute_url(self):
        url = aq_parent(aq_inner(self)).absolute_url()
        identifier = self.getId()
        if identifier is not None:
            url += '/' + identifier
        return url

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

    security.declareProtected(View, 'CMISId')
    def CMISId(self):
        return self._properties['cmis:objectId']

    security.declareProtected(View, 'getCMISBrowser')
    def getCMISBrowser(self):
        # We use this to defeat Acquisition that doesn't work in a python property
        return self._api.context

    security.declareProtected(View, 'created')
    def created(self):
        return to_zope_datetime(self._properties.get('cmis:creationDate'))

    security.declareProtected(View, 'modified')
    def modified(self):
        return to_zope_datetime(self._properties.get('cmis:lastModificationDate'))

    security.declareProtected(View, 'expires')
    def expires(self):
        return DateTime('2499/12/31')

    # IDublinCore implementation
    security.declareProtected(View, 'Identifier')
    Identifier = absolute_url

    security.declareProtected(View, 'Title')
    def Title(self):
        return self._properties.get('cmis:name', u'CMIS Untitled Document')

    security.declareProtected(View, 'Description')
    def Description(self):
        return ''

    security.declareProtected(View, 'Creator')
    def Creator(self):
        return self._properties.get('cmis:createdBy', '')

    security.declareProtected(View, 'CreationDate')
    def CreationDate(self, zone=None):
        if zone is None:
            zone = default_zone
        return self.created().toZone(zone).ISO()

    security.declareProtected(View, 'Date')
    Date = CreationDate

    security.declareProtected(View, 'ModificationDate')
    def ModificationDate(self, zone=None):
        if zone is None:
            zone = default_zone
        return self.modified().toZone(zone).ISO()

    security.declareProtected(View, 'EffectiveDate')
    def EffectiveDate(self, zone=None):
        return 'None'

    security.declareProtected(View, 'ExpirationDate')
    def ExpirationDate(self, zone=None):
        return 'None'

    security.declareProtected(View, 'Format')
    def Format(self):
        return 'text/html'

    security.declareProtected(View, 'Language')
    def Language(self):
        return ''

    security.declareProtected(View, 'Publisher')
    def Publisher(self):
        tool = getToolByName(self, 'portal_metadata', None)

        if tool is not None:
            return tool.getPublisher()

        return 'No publisher'

    security.declareProtected(View, 'Rights')
    def Rights(self):
        return ''

    security.declareProtected(View, 'Subject')
    def Subject(self):
        return tuple()

    security.declareProtected(View, 'Type')
    def Type(self):
        return self.portal_type

    security.declareProtected(View, 'listContributors')
    def listContributors(self):
        return tuple()

    security.declareProtected(View, 'Contributors')
    Contributors = listContributors

    security.declareProtected(View, 'listCreators')
    def listCreators(self):
        creator = self.Creator()
        if creator:
            return (creator,)
        return tuple()

    # Support for portal_type and portal_actions, see IDynamicType
    security.declarePublic('getPortalTypeName')
    getPortalTypeName = Type

    security.declarePublic('getTypeInfo')
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
        try:
            # Fetch document content and display it.
            return self._api.fetch(self), ('@@view',)
        except CMISConnectorError, error:
            error.send(request)
            logger.exception('Error while fetching content from CMIS')
            return CMISErrorTraverser(self.getCMISBrowser())

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

    @property
    def syndication_information(self):
        # Proxy syndication_information setting from the browser
        return self.getCMISBrowser()._getOb('syndication_information', None)

    def publishTraverse(self, request, name):
        # Traverse to a sub CMIS content, or default.
        try:
            content = self._api.traverse(name, self)
            if content is not None:
                return content
        except CMISConnectorError, error:
            error.send(request)
            logger.exception('Error while traversing CMIS repository')
            return CMISErrorTraverser(self.getCMISBrowser())
        return super(CMISFolder, self).publishTraverse(request, name)

    security.declareProtected(View, 'getFolderContents')
    def getFolderContents(self, *args, **kwargs):
        # This is used by Plone templates to list a folder content, and RSS.
        contents = self._api.list(self)
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



