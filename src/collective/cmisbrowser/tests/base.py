# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

import os
import time

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
            'http://localhost:8080/alfresco/s/cmis')
        if method == 'rest':
            self.repository_url = self._repository_url
        else:
            self.repository_url = os.environ.get(
                'CMIS_REPOSITORY_URL_SOAP',
                'http://localhost:8080/alfresco/cmis')
        self.repository_connector = method
        self.repository_name = u''
        self.repository_path = unicode(os.environ.get(
                'CMIS_REPOSITORY_PATH', u''))
        self.repository_cache = 5
        self.repository_user = unicode(os.environ.get(
            'CMIS_REPOSITORY_USER', u''))
        self.repository_password = unicode(os.environ.get(
            'CMIS_REPOSITORY_PASSWORD', u''))
        self.repository_connector = method
        self.folder_view = 'folder_listing'
        self.proxy = None

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

    def configureBrowser(self, browser):
        """Recopy the test settings in a browser.
        """
        for option in ICMISSettings.names():
            if option in self.__dict__:
                setattr(browser, option, self.__dict__[option])

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
            contentString='Contains Documentation about SOAP\nÉtonnant ?',
            contentType='text/plain; charset=UTF-8')
        soap_folder = folder.createFolder('soap')
        soap_folder.createDocumentFromString(
            'specs.txt',
            contentString='Specification\'s SOAP',
            contentType='text/plain')
        info_folder = soap_folder.createFolder('info')
        info_folder.createDocumentFromString(
            'index.html',
            contentString="<p>General Documentation about SOAP</p>",
            contentType='text/html')
        rest_folder = folder.createFolder('rest')
        rest_folder.createDocumentFromString(
            'specs.txt',
            contentString='Specification\'s REST',
            contentType='text/plain')

        # We are now going to browse the testfolder
        self.repository_path = '/testfolder'
        os.environ['CMIS_REPOSITORY_PATH'] = '/testfolder'
        # Make sure the CMIS server have time to reindex it
        # content. This sucks, but we have no other way at the moment.
        time.sleep(60)


@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import collective.cmisbrowser
    load_config('configure.zcml', collective.cmisbrowser)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.cmisbrowser')


setup_product()
ptc.setupPloneSite(products=['collective.cmisbrowser'])

@onsetup
def cmis_test_content():
    settings = TestSettings()
    settings.createTestContent()

cmis_test_content()

class CMISBrowserTestCase(ptc.PloneTestCase):
    pass

