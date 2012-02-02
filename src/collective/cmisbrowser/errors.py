# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.statusmessages.interfaces import IStatusMessage

from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.interface import implements


class CMISConnectorError(ValueError):

    def __init__(self, message, detail=None):
        ValueError.__init__(self, message, detail)
        self.message = message
        self.detail = detail

    def __str__(self):
        message = ': '.join((self.__class__.__name__, self.message))
        if self.detail:
            message = '\n'.join((message, self.detail))
        return message

    def send(self, request):
        IStatusMessage(request).add(self.message, type=u'error')


class CMISErrorTraverser(object):
    # Alternate traverser in case of error. Display an error page.
    implements(IBrowserPublisher)

    def __init__(self, browser):
        self.browser = browser

    def browserDefault(self, request):
        return self.browser, ('@@cmis_error',)

    def publishTraverse(self, request, name):
        return self


