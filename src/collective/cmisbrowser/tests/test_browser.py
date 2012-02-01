# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from collective.cmisbrowser.interfaces import ICMISBrowser
from collective.cmisbrowser.tests.base import CMISBrowserTestCase


class CMISBrowserContentTestCase(CMISBrowserTestCase):

    def test_browser(self):
        self.loginAsPortalOwner()
        browser = self.portal._getOb(
            self.portal.invokeFactory('CMIS Browser', 'browser'))
        self.assertTrue(verifyObject(ICMISBrowser, browser))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CMISBrowserContentTestCase))
    return suite
