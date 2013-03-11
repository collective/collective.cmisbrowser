# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

import unittest

from Acquisition import aq_parent

from zope.interface.verify import verifyObject

from collective.cmisbrowser.cmis.api import CMISZopeAPI, quote
from collective.cmisbrowser.interfaces import ICMISDocument, ICMISFolder, ICMISRootFolder
from collective.cmisbrowser.interfaces import ICMISZopeAPI
from collective.cmisbrowser.tests.base import CMISBrowserTestCase, TestSettings


class APITestCase(CMISBrowserTestCase):
    method = None

    def setUp(self):
        CMISBrowserTestCase.setUp(self)
        self.loginAsPortalOwner()
        self.browser = self.portal._getOb(
            self.portal.invokeFactory('CMIS Browser', 'browser'))
        settings = TestSettings(self.method)
        settings.configureBrowser(self.browser)
        self.api = CMISZopeAPI(self.browser)

    def test_api(self):
        """Test interface and miscealous features.
        """
        self.assertTrue(verifyObject(ICMISZopeAPI, self.api))
        info = self.api.info()
        self.assertTrue('vendorName' in info)
        self.assertTrue('productName' in info)
        self.assertTrue('productVersion' in info)
        self.assertTrue('repositoryName' in info)
        self.assertTrue('repositoryDescription' in info)

    def test_root(self):
        """The API should have a root attribute that represent the
        root of the browser.
        """
        root = self.api.root

        self.assertTrue(verifyObject(ICMISRootFolder, root))
        self.assertEqual(aq_parent(root), self.browser)
        self.assertEqual(root.getId(),None)
        self.assertEqual(
            root.getPhysicalPath(),
            ('', 'plone', 'browser'))
        self.assertEqual(
            root.absolute_url(),
            'http://nohost/plone/browser')
        self.assertEqual(
            root.Identifier(),
            'http://nohost/plone/browser')
        self.assertEqual(root.Type(), 'CMIS Folder')
        self.assertEqual(root.Format(), 'text/html')

    def test_traverse_document(self):
        """Test traverse directly to a document.
        """
        content = self.api.traverse('documentation.txt')
        self.assertTrue(verifyObject(ICMISDocument, content))
        self.assertEqual(aq_parent(content), self.api.root)
        self.assertEqual(content.getId(), 'documentation.txt')
        self.assertEqual(
            content.getPhysicalPath(),
            ('', 'plone', 'browser', 'documentation.txt'))
        self.assertEqual(
            content.absolute_url(),
            'http://nohost/plone/browser/documentation.txt')
        self.assertEqual(
            content.Identifier(),
            'http://nohost/plone/browser/documentation.txt')
        self.assertEqual(content.Type(), 'CMIS Document')
        self.assertEqual(content.Format(), 'text/plain; charset=UTF-8')

    def test_traverse_folder(self):
        """Test traverse directly to a folder.
        """
        folder = self.api.traverse('soap')
        self.assertTrue(verifyObject(ICMISFolder, folder))
        self.assertEqual(aq_parent(folder), self.api.root)
        self.assertEqual(folder.getId(), 'soap')
        self.assertEqual(
            folder.getPhysicalPath(),
            ('', 'plone', 'browser', 'soap'))
        self.assertEqual(
            folder.absolute_url(),
            'http://nohost/plone/browser/soap')
        self.assertEqual(
            folder.Identifier(),
            'http://nohost/plone/browser/soap')
        self.assertEqual(folder.Type(), 'CMIS Folder')
        self.assertEqual(folder.Format(), 'text/html')

        # A Folder can list its own content
        contents = folder.getFolderContents()
        self.assertEqual(len(contents), 2)
        contents = sorted(contents, key=lambda c: c.getId())
        self.assertEqual(
            map(lambda c: c.getId(), contents),
            ['info', 'specs.txt'])
        self.assertEqual(
            map(lambda c: c.Type(), contents),
            ['CMIS Folder', 'CMIS Document'])
        self.assertEqual(
            map(lambda c: c.Format(), contents),
            ['text/html', 'text/plain'])
        self.assertEqual(
            map(lambda c: c.absolute_url(), contents),
            ['http://nohost/plone/browser/soap/info',
             'http://nohost/plone/browser/soap/specs.txt'])

    def test_traverse_notfound(self):
        """Test traverse to an item that doesn't exists.
        """
        content = self.api.traverse('nowhere')
        self.assertEqual(content, None)

    def test_traverse_folder_to_document(self):
        """Test traverse to a document from a container.
        """
        parent = self.api.traverse('soap')
        self.assertTrue(verifyObject(ICMISFolder, parent))

        content = self.api.traverse('specs.txt', parent)
        self.assertTrue(verifyObject(ICMISDocument, content))
        self.assertEqual(aq_parent(content), parent)
        self.assertEqual(content.getId(), 'specs.txt')
        self.assertEqual(
            content.getPhysicalPath(),
            (    '', 'plone', 'browser', 'soap', 'specs.txt'))
        self.assertEqual(
            content.absolute_url(),
            'http://nohost/plone/browser/soap/specs.txt')
        self.assertEqual(
            content.Identifier(),
            'http://nohost/plone/browser/soap/specs.txt')
        self.assertEqual(content.Type(), 'CMIS Document')
        self.assertEqual(content.Format(), 'text/plain')

    def test_traverse_folder_to_folder(self):
        """Test traverse to a container from a container.
        """
        parent = self.api.traverse('soap')
        self.assertTrue(verifyObject(ICMISFolder, parent))

        folder = self.api.traverse('info', parent)
        self.assertTrue(verifyObject(ICMISFolder, folder))
        self.assertEqual(aq_parent(folder), parent)
        self.assertEqual(folder.getId(), 'info')
        self.assertEqual(
            folder.getPhysicalPath(),
            ('', 'plone', 'browser', 'soap', 'info'))
        self.assertEqual(
            folder.absolute_url(),
            'http://nohost/plone/browser/soap/info')
        self.assertEqual(
            folder.Identifier(),
            'http://nohost/plone/browser/soap/info')
        self.assertEqual(folder.Type(), 'CMIS Folder')
        self.assertEqual(folder.Format(), 'text/html')

        # A Folder can list its own content
        contents = folder.getFolderContents()
        self.assertEqual(len(contents), 1)
        contents = sorted(contents, key=lambda c: c.getId())
        self.assertEqual(
            map(lambda c: c.getId(), contents),
            ['index.html'])
        self.assertEqual(
            map(lambda c: c.Type(), contents),
            ['CMIS Document'])
        self.assertEqual(
            map(lambda c: c.Format(), contents),
            ['text/html'])
        self.assertEqual(
            map(lambda c: c.absolute_url(), contents),
            ['http://nohost/plone/browser/soap/info/index.html'])

    def test_search_score_support(self):
        """Test search feature, with score feature on, quoting off.
        NOT EVERY CMIS REPOSITORY SUPPORTS IT.
        """
        results = self.api.search('soap')
        results = sorted(results, key=lambda c: c.getId())
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 3)
        self.assertEqual(
            map(lambda c: c.getId(), results),
            ['documentation.txt', 'index.html', 'specs.txt', ])
        self.assertEqual(
            map(lambda c: c.Type(), results),
            ['CMIS Document', 'CMIS Document', 'CMIS Document'])
        self.assertEqual(
            map(lambda c: c.absolute_url(), results),
            ['http://nohost/plone/browser/documentation.txt',
             'http://nohost/plone/browser/soap/info/index.html',
             'http://nohost/plone/browser/soap/specs.txt'])

    def test_search_no_score_support(self):
        """Test search feature with score feature off.
        """
        results = self.api.search('soap', scorable=False)
        results = sorted(results, key=lambda c: c.getId())
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 3)
        self.assertEqual(
            map(lambda c: c.getId(), results),
            ['documentation.txt', 'index.html', 'specs.txt', ])
        self.assertEqual(
            map(lambda c: c.Type(), results),
            ['CMIS Document', 'CMIS Document', 'CMIS Document'])
        self.assertEqual(
            map(lambda c: c.absolute_url(), results),
            ['http://nohost/plone/browser/documentation.txt',
             'http://nohost/plone/browser/soap/info/index.html',
             'http://nohost/plone/browser/soap/specs.txt'])

    def test_search_unicode_quotable_support(self):
        """Test search feature with an unicode entry.
        """
        results = self.api.search(u"Étonnant", quotable=True)
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 1)
        self.assertEqual(
            map(lambda c: c.getId(), results),
            ['documentation.txt'])
        self.assertEqual(
            map(lambda c: c.Type(), results),
            ['CMIS Document'])
        self.assertEqual(
            map(lambda c: c.absolute_url(), results),
            ['http://nohost/plone/browser/documentation.txt'])

    def test_search_unicode_support(self):
        """Test search feature with an unicode entry.
        """
        results = self.api.search(u"Étonnant")
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 1)
        self.assertEqual(
            map(lambda c: c.getId(), results),
            ['documentation.txt'])
        self.assertEqual(
            map(lambda c: c.Type(), results),
            ['CMIS Document'])
        self.assertEqual(
            map(lambda c: c.absolute_url(), results),
            ['http://nohost/plone/browser/documentation.txt'])

    def test_search_escape_quotable_support(self):
        """Test search feature with an entry that have an ', and
        quoting. NOT ALL CMIS REPOSITORY SUPPORTS IT.
        """
        results = self.api.search(r"specification's", quotable=True)
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 2)
        self.assertEqual(
            map(lambda c: c.getId(), results),
            ['specs.txt', 'specs.txt'])
        self.assertEqual(
            map(lambda c: c.Type(), results),
            ['CMIS Document', 'CMIS Document'])
        self.assertEqual(
            map(lambda c: c.absolute_url(), results),
            ['http://nohost/plone/browser/soap/specs.txt',
             'http://nohost/plone/browser/rest/specs.txt'])

    def test_search_escape_hacker_quotable_support(self):
        """Test search feature with an entry that have an \', quoting
        on.
        """
        results = self.api.search(r"specification\'s", quotable=True)
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 2)
        self.assertEqual(
            map(lambda c: c.getId(), results),
            ['specs.txt', 'specs.txt'])
        self.assertEqual(
            map(lambda c: c.Type(), results),
            ['CMIS Document', 'CMIS Document'])
        self.assertEqual(
            map(lambda c: c.absolute_url(), results),
            ['http://nohost/plone/browser/soap/specs.txt',
             'http://nohost/plone/browser/rest/specs.txt'])

    def test_search_escape_no_quotable_support(self):
        """Test search feature with an entry that have an ', and
        quoting. NOT ALL CMIS REPOSITORY SUPPORTS IT.
        """
        results = self.api.search(r"specification's")
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 0)

    def test_search_escape_hacker_no_quotable_support(self):
        """Test search feature with an entry that have an \', quoting
        on.
        """
        results = self.api.search(r"specification\'s")
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 0)



class RESTAPITestCase(APITestCase):
    method = 'rest'


class SOAPAPITestCase(APITestCase):
    method = 'soap'


class QuoteTestCase(unittest.TestCase):

    def test_escape(self):
        self.assertEqual(
            quote(r"This is some text"), r"This is some text")
        self.assertEqual(
            quote(r"This is 'some text"), r"This is \'some text")
        self.assertEqual(
            quote(r"This is \'some text"), r"This is \'some text")
        self.assertEqual(
            quote(r"\'This is some text'"), r"\'This is some text\'")
        self.assertEqual(
            quote(r"'This is some text'"), r"\'This is some text\'")
        self.assertEqual(
            quote(r"This is \\'some text"), r"This is \\\'some text")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuoteTestCase))
    suite.addTest(unittest.makeSuite(RESTAPITestCase))
    suite.addTest(unittest.makeSuite(SOAPAPITestCase))
    return suite
