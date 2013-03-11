# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

from operator import itemgetter
import unittest

from zope.component import queryAdapter
from zope.interface.verify import verifyObject
from collective.cmisbrowser.errors import CMISConnectorError
from collective.cmisbrowser.interfaces import ICMISConnector
from collective.cmisbrowser.tests.base import CMISBrowserTestCase, TestSettings
from collective.cmisbrowser.interfaces import ICMISFileResult

from zExceptions import NotFound


class ConnectorTestCase(CMISBrowserTestCase):
    method = None

    def setUp(self):
        CMISBrowserTestCase.setUp(self)
        self.settings = TestSettings(self.method)

    def test_start(self):
        """Test start, that retrieve the root of the connector.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        self.assertTrue(verifyObject(ICMISConnector, connector))

        root = connector.start()
        self.assertTrue(isinstance(root, dict))
        self.assertEqual(root['cmis:name'], 'testfolder')
        self.assertEqual(root['cmis:path'], '/testfolder')
        self.assertEqual(root['cmis:objectTypeId'], 'cmisbrowser:root')
        self.assertEqual(root['cmis:baseTypeId'], 'cmis:folder')

    def test_get_object_by_path_document(self):
        """Test get_object_by_path fetching a document.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        connector.start()

        item = connector.get_object_by_path('/testfolder/soap/specs.txt')
        self.assertTrue(isinstance(item, dict))
        self.assertTrue('cmis:objectId' in item)
        self.assertEqual(item['cmis:name'], 'specs.txt')
        self.assertEqual(item['cmis:objectTypeId'], 'cmis:document')
        self.assertEqual(item['cmis:baseTypeId'], 'cmis:document')
        if 'cmisbrowser:identifier' in item:
            self.assertEqual(item['cmisbrowser:identifier'], 'specs.txt')

    def test_get_object_by_path_folder(self):
        """Test get_object_by_path fetching a folder.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        connector.start()

        folder = connector.get_object_by_path('/testfolder/soap')
        self.assertTrue(isinstance(folder, dict))
        self.assertTrue('cmis:objectId' in folder)
        self.assertEqual(folder['cmis:name'], 'soap')
        self.assertEqual(folder['cmis:objectTypeId'], 'cmis:folder')
        self.assertEqual(folder['cmis:baseTypeId'], 'cmis:folder')
        if 'cmisbrowser:identifier' in folder:
            self.assertEqual(folder['cmisbrowser:identifier'], 'soap')

    def test_get_object_by_path_unexisting(self):
        """Test get_object_by_path fetching something that doesn't exit.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        connector.start()

        self.assertRaises(
            NotFound,
            connector.get_object_by_path,
            '/testfolder/nothing')

    def test_get_object_by_cmis_id(self):
        """Test get_object_by_cmis_id.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        connector.start()

        original = connector.get_object_by_path('/testfolder/soap/specs.txt')
        item = connector.get_object_by_cmis_id(original['cmis:objectId'])
        self.assertTrue(isinstance(item, dict))
        self.assertEqual(item['cmis:objectId'], original['cmis:objectId'])
        self.assertEqual(item['cmis:name'], 'specs.txt')
        self.assertEqual(item['cmis:objectTypeId'], 'cmis:document')
        self.assertEqual(item['cmis:baseTypeId'], 'cmis:document')
        if 'cmisbrowser:identifier' in item:
            self.assertEqual(item['cmisbrowser:identifier'], 'specs.txt')

    def test_get_object_by_cmis_id_unexisting(self):
        """Test get_object_by_cmis_id with an invalid/expired identifier.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        connector.start()

        self.assertRaises(
            CMISConnectorError,
            connector.get_object_by_cmis_id,
            'lalala')

    def test_get_object_parent(self):
        """Test get_object_parent.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        connector.start()

        item = connector.get_object_by_path('/testfolder/soap/specs.txt')
        parent = connector.get_object_parent(item['cmis:objectId'])
        self.assertTrue(isinstance(parent, tuple))
        self.assertEqual(len(parent), 2)
        folder, name = parent
        self.assertEqual(name, 'specs.txt')
        self.assertTrue('cmis:objectId' in folder)
        self.assertEqual(folder['cmis:name'], 'soap')
        self.assertEqual(folder['cmis:objectTypeId'], 'cmis:folder')
        self.assertEqual(folder['cmis:baseTypeId'], 'cmis:folder')
        if 'cmisbrowser:identifier' in folder:
            self.assertEqual(folder['cmisbrowser:identifier'], 'soap')

    def test_get_object_parent_unexisting(self):
        """Test get_object_parent with an invalid identifier.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        connector.start()

        self.assertRaises(
            CMISConnectorError,
            connector.get_object_parent,
            'lalala')

    def test_get_object_parents(self):
        """Test get_object_parents.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        connector.start()

        item = connector.get_object_by_path('/testfolder/soap/info/index.html')
        parents = connector.get_object_parents(item['cmis:objectId'])
        self.assertTrue(isinstance(parents, tuple))
        self.assertEqual(len(parents), 2)
        folders, name = parents
        self.assertTrue(isinstance(folders, list))
        self.assertEqual(len(folders), 3)
        self.assertEqual(
            map(itemgetter('cmis:name'), folders),
            ['info', 'soap', 'testfolder'])
        self.assertEqual(
            map(itemgetter('cmis:objectTypeId'), folders),
            ['cmis:folder', 'cmis:folder', 'cmisbrowser:root'])
        self.assertEqual(
            map(lambda c: c.get('cmis:objectId') is not None, folders),
            [True, True, True])

    def test_get_object_children(self):
        """Test get_object_children.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        connector.start()

        item = connector.get_object_by_path('/testfolder')
        children = connector.get_object_children(item['cmis:objectId'])
        self.assertTrue(isinstance(children, list))
        self.assertEqual(len(children), 4)
        children = sorted(children, key=itemgetter('cmis:name'))
        self.assertEqual(
            map(itemgetter('cmis:name'), children),
            ['documentation.txt', 'hello.html', 'rest', 'soap'])
        self.assertEqual(
            map(itemgetter('cmis:objectTypeId'), children),
            ['cmis:document', 'cmis:document', 'cmis:folder', 'cmis:folder'])
        self.assertEqual(
            map(lambda c: c.get('cmis:objectId') is not None, children),
            [True, True, True, True])

    def test_get_object_content(self):
        """Test get_object_content.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        connector.start()
        item = connector.get_object_by_path('/testfolder/hello.html')
        content = connector.get_object_content(item['cmis:objectId'])

        self.assertTrue(verifyObject(ICMISFileResult, content))
        self.assertEqual(content.filename, 'hello.html')
        self.assertEqual(content.mimetype, 'text/html')
        self.assertEqual(content.length, 42)

    def test_query_for_objects(self):
        """Test query_for_objects.
        """
        connector = queryAdapter(self.settings, ICMISConnector, self.method)
        root = connector.start()

        contents = connector.query_for_objects(
            "SELECT R.* FROM cmis:document R WHERE IN_TREE('%s')" % root['cmis:objectId'])
        self.assertTrue(isinstance(contents, list))
        self.assertEqual(len(contents), 5)
        self.assertEqual(
            sorted(map(itemgetter('cmis:name'), contents)),
            ['documentation.txt', 'hello.html', 'index.html', 'specs.txt', 'specs.txt'])


class RESTConnectorTestCase(ConnectorTestCase):
    method = 'rest'

class SOAPConnectorTestCase(ConnectorTestCase):
    method = 'soap'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RESTConnectorTestCase))
    suite.addTest(unittest.makeSuite(SOAPConnectorTestCase))
    return suite

