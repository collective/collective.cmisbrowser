# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from collective.cmisbrowser.interfaces import ICMISBrowser
from plone.app.content.item import Item
from zope.component.factory import Factory
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

_ = MessageFactory('collective.cmisbrowser')


class CMISBrowser(Item):
    implements(ICMISBrowser)
    portal_type = "CMIS Browser"

    url = FieldProperty(ICMISBrowser['url'])
    name = FieldProperty(ICMISBrowser['name'])
    user = FieldProperty(ICMISBrowser['user'])
    password = FieldProperty(ICMISBrowser['password'])
    proxy = FieldProperty(ICMISBrowser['proxy'])


CMISBrowserFactory = Factory(CMISBrowser, title=_(u"Create CMIS Browser"))
