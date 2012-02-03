# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging
import uuid

from ZPublisher.BaseRequest import DefaultPublishTraverse

from plone.app.content.container import Container
from zope.component.factory import Factory
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.schema.fieldproperty import FieldProperty

from collective.cmisbrowser.cmis.api import CMISZopeAPI
from collective.cmisbrowser.errors import CMISConnectorError
from collective.cmisbrowser.errors import CMISErrorTraverser
from collective.cmisbrowser.interfaces import ICMISBrowser

_ = MessageFactory('collective.cmisbrowser')


logger = logging.getLogger('collective.cmisbrowser')


class CMISTraverser(object):
    implements(IBrowserPublisher)

    def __init__(self, browser):
        self.browser = browser

    def get_api(self):
        # This will always be called only one time.
        return CMISZopeAPI(self.browser)

    def browserDefault(self, request):
        try:
            return self.get_api().root, ('@@view',)
        except CMISConnectorError, error:
            error.send(request)
            logger.exception('Error while accessing CMIS repository')
            return self.browser, ('@@cmis_error',)

    def publishTraverse(self, request, name):
        try:
            content = self.get_api().traverse(name)
            if content is not None:
                return content
        except CMISConnectorError, error:
            error.send(request)
            logger.exception('Error while accessing CMIS repository')
            return CMISErrorTraverser(self.browser)
        default = DefaultPublishTraverse(self.browser, request)
        return default.publishTraverse(request, name)


class CMISBrowser(Container):
    implements(ICMISBrowser)
    portal_type = "CMIS Browser"
    # Make sure to disable comments
    allow_discussion = False

    repository_url = FieldProperty(ICMISBrowser['repository_url'])
    repository_name = FieldProperty(ICMISBrowser['repository_name'])
    repository_path = FieldProperty(ICMISBrowser['repository_path'])
    repository_user = FieldProperty(ICMISBrowser['repository_user'])
    repository_password = FieldProperty(ICMISBrowser['repository_password'])
    folder_view = FieldProperty(ICMISBrowser['folder_view'])
    proxy = FieldProperty(ICMISBrowser['proxy'])
    _uid = None

    def UID(self):
        if self._uid is None:
            self._uid = str(uuid.uuid1())
        return self._uid

    def browserDefault(self, request):
        return CMISTraverser(self).browserDefault(request)

    def publishTraverse(self, request, name):
        return CMISTraverser(self).publishTraverse(request, name)

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


def browser_cloned_event(browser, event):
    # When we copy a browser, we get a new one. Reset its uid.
    browser._uid = None
