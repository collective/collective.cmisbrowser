# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from plone.app.content.interfaces import INameFromTitle
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface

_ = MessageFactory('collective.cmisbrowser')


class ICMISSettings(Interface):

    url = schema.URI(
        title=_(u'CMIS repository URI'))
    name = schema.TextLine(
        title=_(u'CMIS repository name'))
    user = schema.TextLine(
        title=_(u'User to authenticate with'),
        required=False)
    password = schema.Password(
        title=_(u'Password to authenticate with'),
        required=False)
    proxy = schema.URI(
        title=_(u'HTTP-Proxy to use to access CMIS repository'),
        required=False)


class ICMISConnection(Interface):
    pass


class ICMISConnector(Interface):
    """Connect to a CMIS repository
    """

    def connect(setting):
        """Return an active connection to a CMIS connector.
        """


class ICMISFolderBrowser(Interface):
    """A Browsed folder.
    """


class ICMISBrowser(ICMISConnector, ICMISFolderBrowser, INameFromTitle, ICMISSettings):
    """A Browser.
    """
