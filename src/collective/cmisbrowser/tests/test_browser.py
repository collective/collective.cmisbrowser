# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from collective.cmisbrowser.interfaces import ICMISBrowser
from collective.cmisbrowser.interfaces import ICMISSettings
from collective.cmisbrowser.tests.base import CMISBrowserTestCase, TestSettings


class CMISBrowserContentTestCase(CMISBrowserTestCase):

    def setUp(self):
        CMISBrowserTestCase.setUp(self)
        self.loginAsPortalOwner()
        self.browser = self.portal._getOb(
            self.portal.invokeFactory('CMIS Browser', 'browser'))

    def test_browser(self):
        """Verify interface from the browser.
        """
        self.assertTrue(verifyObject(ICMISBrowser, self.browser))
        self.assertTrue(verifyObject(ICMISSettings, self.browser))
        self.assertTrue(verifyObject(ICMISSettings, TestSettings()))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CMISBrowserContentTestCase))
    return suite
