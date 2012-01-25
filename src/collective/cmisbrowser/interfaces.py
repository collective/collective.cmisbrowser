# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface
from zope import schema


class ICMISSetting(Interface):

    url = schema.URI(
        title=u'CMIS repository URI')
    user = schema.TextLine(
        title=u'User to authenticate with',
        required=False)
    password = schema.TextLine(
        title=u'Password to authenticate with',
        required=False)
    proxy = schema.URI(
        title=u'HTTP-Proxy to use to access CMIS repository')


class ICMISConnection(Interface):
    pass


class ICMISConnector(Interface):

    def connect():
        """Return an active connection to a CMIS connector.
        """
