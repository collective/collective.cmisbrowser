# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os

try:
    from Zope2.App.zcml import load_config
except ImportError:
    from Products.Five.zcml import load_config
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc

from cmislib.model import CmisClient
import cmislib.exceptions

from zope.cachedescriptors.property import Lazy
from zope.interface import implements
from collective.cmisbrowser.interfaces import ICMISSettings


class TestSettings(object):
    """Those are test settings that can be used with the browser to
    connect to a test server. This provides extra facilities to create
    some test content as well.
    """
    implements(ICMISSettings)

    def __init__(self, method='soap'):
        assert method in ('soap', 'rest')
        # Private URL used to create test content
        self._repository_url = os.environ.get(
            'CMIS_REPOSITORY_URL_REST',
            'http://localhost/alfresco/s/cmis')
        if method == 'rest':
            self.repository_url = self._repository_url
        else:
            self.repository_url = os.environ.get(
                'CMIS_REPOSITORY_URL_SOAP',
                'http://localhost/alfresco/cmis')
        self.repository_name = ''
        self.repository_path = ''
        self.repository_cache = 5
        self.repository_user = os.environ.get(
            'CMIS_REPOSITORY_USER', '')
        self.repository_password = os.environ.get(
            'CMIS_REPOSITORY_PASSWORD', '')
        self.repository_connector = method
        self.folder_view = 'folder_listing'
        self.proxy = ''

    def UID(self):
        return '42'

    @Lazy
    def _repository(self):
        client = CmisClient(
            self._repository_url,
            self.repository_user,
            self.repository_password)
        repositories = client.getRepositories()
        assert len(repositories) == 1
        identifier = repositories[0]['repositoryId']
        return client.getRepository(identifier)

    @Lazy
    def _repository_root(self):
        repository = self._repository
        return repository.getRootFolder()

    def createTestContent(self):
        """Create a test folder, /testfolder, with the following
        structure:

        /testfolder@
           |- hello.html
           |- documentation.txt
           |- soap@
           |    |- info@
           |    |    \- index.html
           |    \- specs.txt
           \- rest@
                \- specs.txt
        """

        try:
            # Clean existing test folder.
            folder = self._repository.getObjectByPath('/testfolder')
        except cmislib.exceptions.ObjectNotFoundException:
            pass
        else:
            folder.deleteTree()

        folder = self._repository_root.createFolder('testfolder')
        folder.createDocumentFromString(
            'hello.html',
            contentString='<p>Hello, this some basic test content</p>',
            contentType='text/html')
        folder.createDocumentFromString(
            'documentation.txt',
            contentString='Contains Documentation about SOAP',
            contentType='text/plain')
        soap_folder = folder.createFolder('soap')
        soap_folder.createDocumentFromString(
            'specs.txt',
            contentString='Specification SOAP',
            contentType='text/plain')
        info_folder = soap_folder.createFolder('info')
        info_folder.createDocumentFromString(
            'index.html',
            contentString="<p>General Documentation about SOAP</p>",
            contentType='text/html')
        rest_folder = folder.createFolder('rest')
        rest_folder.createDocumentFromString(
            'specs.txt',
            contentString='Specification REST',
            contentType='text/plain')

        # We are now going to browse the testfolder
        self.repository_path = '/testfolder'



@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import collective.cmisbrowser
    load_config('configure.zcml', collective.cmisbrowser)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.cmisbrowser')


setup_product()
ptc.setupPloneSite(products=['collective.cmisbrowser'])

class CMISBrowserTestCase(ptc.PloneTestCase):
    pass

