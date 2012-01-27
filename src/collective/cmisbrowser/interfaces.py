# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.publisher.interfaces.browser import IBrowserPublisher
from plone.app.content.interfaces import INameFromTitle
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface

_ = MessageFactory('collective.cmisbrowser')


class ICMISSettings(Interface):

    repository_url = schema.URI(
        title=_(u'CMIS repository URI'))
    repository_name = schema.TextLine(
        title=_(u'CMIS repository name'),
        required=False)
    repository_path = schema.TextLine(
        title=_(u'CMIS start folder path'),
        description=_(u'Folder in the CMIS repository at which the browser should start'),
        required=False)
    repository_user = schema.TextLine(
        title=_(u'User to access CMIS repository'),
        required=False)
    repository_password = schema.Password(
        title=_(u'Password to access CMIS repository'),
        required=False)
    proxy = schema.URI(
        title=_(u'HTTP-Proxy to use to access CMIS repository'),
        required=False)


class ICMISConnector(Interface):
    """Connect to a CMIS repository.
    """


class ICMISBrowserAware(IBrowserPublisher):
    """Object that can become a CMIS folder browser.
    """


class ICMISDocument(Interface):
    """A browsed document.
    """


class ICMISFolder(ICMISDocument, ICMISBrowserAware):
    """A browsed folder.
    """


class ICMISBrowser(ICMISBrowserAware, INameFromTitle, ICMISSettings):
    """A Browser.
    """

    def connect():
        """Return a connector to the current CMIS repository.
        """
