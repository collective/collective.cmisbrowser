# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

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
        settings = TestSettings('soap')
        self.assertTrue(verifyObject(ICMISBrowser, self.browser))
        self.assertTrue(verifyObject(ICMISSettings, self.browser))
        self.assertTrue(verifyObject(ICMISSettings, settings))
        settings.configureBrowser(self.browser)
        self.assertEqual(self.browser.repository_connector, 'soap')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CMISBrowserContentTestCase))
    return suite
