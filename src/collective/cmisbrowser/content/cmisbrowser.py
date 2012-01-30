# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from collective.cmisbrowser.interfaces import ICMISBrowser, ICMISConnector
from collective.cmisbrowser.interfaces import CMISConnectorError
from plone.app.content.item import Item
from zope.component.factory import Factory
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from Acquisition import aq_inner
from ZPublisher.BaseRequest import DefaultPublishTraverse

_ = MessageFactory('collective.cmisbrowser')


logger = logging.getLogger('collective.cmisbrowser')


class CMISErrorTraverser(object):
    # Alternate traverser in case of error. Display an error page.
    implements(IBrowserPublisher)

    def __init__(self, browser):
        self.browser = browser

    def browserDefault(self, request):
        return self.browser, ('@@view',)

    def publishTraverse(self, request, name):
        return self


class CMISTraverser(object):
    implements(IBrowserPublisher)

    def __init__(self, browser):
        self.browser = browser
        self.connector = browser.connect()

    def browserDefault(self, request):
        try:
            root = self.connector.start().__of__(self.browser)
            return root, ('@@view',)
        except CMISConnectorError:
            logger.exception('Error while accessing CMIS repository')
            return self.browser, ('@@view',)

    def publishTraverse(self, request, name):
        try:
            root = self.connector.start().__of__(self.browser)
            path = root._properties.get('cmis:path')
            if path:
                path = path.rstrip('/') + '/' + name
                content = self.connector.get_object_by_path(path)
                return content.__of__(root)
        except CMISConnectorError:
            logger.exception('Error while accessing CMIS repository')
            return CMISErrorTraverser(self.browser)
        default = DefaultPublishTraverse(self.browser, request)
        return default.publishTraverse(request, name)


class CMISBrowser(Item):
    implements(ICMISBrowser)
    portal_type = "CMIS Browser"

    repository_url = FieldProperty(ICMISBrowser['repository_url'])
    repository_name = FieldProperty(ICMISBrowser['repository_name'])
    repository_path = FieldProperty(ICMISBrowser['repository_path'])
    repository_user = FieldProperty(ICMISBrowser['repository_user'])
    repository_password = FieldProperty(ICMISBrowser['repository_password'])
    folder_view = FieldProperty(ICMISBrowser['folder_view'])
    proxy = FieldProperty(ICMISBrowser['proxy'])

    def connect(self):
        return ICMISConnector(self)

    def getCMISBrowser(self):
        return aq_inner(self)

    def browserDefault(self, request):
        return CMISTraverser(self).browserDefault(request)

    def publishTraverse(self, request, name):
        return CMISTraverser(self).publishTraverse(request, name)

    def getLocallyAllowedTypes(self):
        # You don't have the right to add anything here.
        return []


CMISBrowserFactory = Factory(CMISBrowser, title=_(u"Create CMIS Browser"))

