# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from collective.cmisbrowser.interfaces import ICMISBrowser
from collective.cmisbrowser.interfaces import ICMISConnector
from plone.app.content.item import Item
from zope.component.factory import Factory
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from ZPublisher.BaseRequest import DefaultPublishTraverse

_ = MessageFactory('collective.cmisbrowser')



class CMISTraverser(object):
    implements(IBrowserPublisher)

    def __init__(self, browser):
        self.browser = browser
        self.connector = browser.connect()
        self.context = self.connector.start().__of__(browser)

    def browserDefault(self, request):
        return self.context, ('@@view',)

    def publishTraverse(self, request, name):
        path = self.context._properties.get('cmis:path')
        if path:
            path = path.rstrip('/') + '/' + name
            content = self.connector.get_object_by_path(path)
            return content.__of__(self.context)
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
    proxy = FieldProperty(ICMISBrowser['proxy'])

    def connect(self):
        return ICMISConnector(self)

    def browserDefault(self, request):
        return CMISTraverser(self).browserDefault(request)

    def publishTraverse(self, request, name):
        return CMISTraverser(self).publishTraverse(request, name)


CMISBrowserFactory = Factory(CMISBrowser, title=_(u"Create CMIS Browser"))

