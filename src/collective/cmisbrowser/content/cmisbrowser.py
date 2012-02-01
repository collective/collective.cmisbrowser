# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from collective.cmisbrowser.interfaces import ICMISBrowser
from collective.cmisbrowser.interfaces import CMISConnectorError
from collective.cmisbrowser.cmis.api import CMISObjectAPI
from plone.app.content.container import Container
from zope.component.factory import Factory
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

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
        self.api = CMISObjectAPI(browser)

    def browserDefault(self, request):
        return self.api.root, ('@@view',)

    def publishTraverse(self, request, name):
        content = self.api.traverse(name)
        if content is not None:
            return content
        default = DefaultPublishTraverse(self.browser, request)
        return default.publishTraverse(request, name)


class CMISBrowser(Container):
    implements(ICMISBrowser)
    portal_type = "CMIS Browser"

    repository_url = FieldProperty(ICMISBrowser['repository_url'])
    repository_name = FieldProperty(ICMISBrowser['repository_name'])
    repository_path = FieldProperty(ICMISBrowser['repository_path'])
    repository_user = FieldProperty(ICMISBrowser['repository_user'])
    repository_password = FieldProperty(ICMISBrowser['repository_password'])
    folder_view = FieldProperty(ICMISBrowser['folder_view'])
    proxy = FieldProperty(ICMISBrowser['proxy'])

    def browserDefault(self, request):
        try:
            return CMISTraverser(self).browserDefault(request)
        except CMISConnectorError:
            logger.exception('Error while accessing CMIS repository')
            return self.browser, ('@@view',)

    def publishTraverse(self, request, name):
        try:
            return CMISTraverser(self).publishTraverse(request, name)
        except CMISConnectorError:
            logger.exception('Error while accessing CMIS repository')
            return CMISErrorTraverser(self.browser)

    # Implement IContrainTypes, you cannot add anything here.

    def getConstrainTypesMode(self):
        return 1

    def getLocallyAllowedTypes(self):
        return []

    def getImmediatelyAddableTypes(self):
        return []

    def getDefaultAddableTypes(self):
        return []

    def allowedContentTypes(self):
        return []


CMISBrowserFactory = Factory(CMISBrowser, title=_(u"Create CMIS Browser"))

