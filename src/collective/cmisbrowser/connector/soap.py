# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

import suds
import subprocess
import urllib2
import time

from zExceptions import NotFound

from plone.memoize import ram
from zope.interface import implements
from zope.cachedescriptors.property import Lazy

from collective.cmisbrowser.cmis.result import CMISFileResult
from collective.cmisbrowser.errors import CMISConnectorError
from collective.cmisbrowser.interfaces import ICMISConnector


def indent_xml(xml):
    try:
        # This is used for debug.
        stdout, stderr = subprocess.Popen(
            'xmlindent',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE).communicate(
            input=xml)
    except OSError:
        # We don't have xmlindent, don't indent the xml.
        return xml
    return stdout


class SOAPConnectorError(CMISConnectorError):
    pass


# Usefull decorators

def soap_error(object_lookup=False):

    def error_matcher(wrapped):

        def wrapper(self, *args, **kwargs):
            try:
                return wrapped(self, *args, **kwargs)
            except urllib2.URLError, error:
                if isinstance(error.args[0], tuple):
                    raise SOAPConnectorError(
                        u'Network transport error: %s' % str(error.args[0][1]))
                raise SOAPConnectorError(
                    u'Network error: %s' % str(error.args[0]))
            except suds.transport.TransportError, error:
                raise SOAPConnectorError(
                    u'HTTP transport error, code %d' % error.httpcode,
                    indent_xml(error.fp.read()))
            except suds.WebFault, error:
                cmis_error = getattr(getattr(error.fault, 'detail', None), 'cmisFault', None)
                if object_lookup and cmis_error is not None:
                    # In case of object not found, we convert to a Zope error
                    if (cmis_error.type == 'objectNotFound' or
                        (not self.have_object_not_found_exception and cmis_error.type == 'invalidArgument')):
                        raise NotFound()
                raise SOAPConnectorError(
                    error.fault.faultstring,
                    error.document.str())

        return wrapper

    return error_matcher

def soap_cache(wrapped):

    def get_cache_key(method, self, id_or_path, *args, **kwargs):
        return '#'.join((
                self._settings.UID(),
                self._repository_id,
                id_or_path.encode('ascii', 'xmlcharrefreplace'),
                str(time.time() // (self._settings.repository_cache * 60))))

    return ram.cache(get_cache_key)(wrapped)


# Utility to convert SOAP-structure to simple dict.

def properties_to_dict(properties, prefix=None, root=False, identifier=None):
    values = []
    entry = properties.properties.__dict__

    def serialize(value):
        definition_id = value._propertyDefinitionId
        if prefix is not None and definition_id.startswith(prefix):
            definition_id = definition_id[len(prefix):]
        data = getattr(value, 'value', [])
        if len(data):
            # XXX We need to do something to support multi-values here
            values.append((definition_id, data[0]))

    for key in entry.keys():
        if not key.startswith('property'):
            continue
        value = entry.get(key, [])
        if isinstance(value, list):
            map(serialize, value)
        else:
            serialize(value)
    result = dict(values)
    if root:
        if isinstance(root, bool) or root == result['cmis:objectId']:
            result['cmis:objectTypeId'] = 'cmisbrowser:root'
    if identifier:
        result['cmisbrowser:identifier'] = identifier
    return result


class SOAPClient(object):
    """This provide a direct access to the SOAP client, who are cached.
    """

    def __init__(self, settings):
        if not settings.repository_url:
            # Settings are invalid.
            raise NotFound()
        self.settings = settings
        self.proxies = {}
        if settings.proxy:
            self.proxies['http'] = settings.proxy
            self.proxies['https'] = settings.proxy

        if self.settings.repository_user:
            if self.settings.repository_password is None:
                raise SOAPConnectorError(
                    u'Settings specify user and not password.')

    def _create_client(self, service):
        """Create an authenticated SOAP client to access an SOAP
        service.
        """
        # We must specify service and port for Nuxeo
        client = suds.client.Client(
            '/'.join((self.settings.repository_url, service)) + '?wsdl',
            proxy=self.proxies,
            service=service,
            port=service + 'Port',
            cachingpolicy=1)
        if self.settings.repository_user:
            # Timestamp must be included, and be first for Alfresco.
            auth = suds.wsse.Security()
            auth.tokens.append(suds.wsse.Timestamp(validity=300))
            auth.tokens.append(suds.wsse.UsernameToken(
                    self.settings.repository_user,
                    self.settings.repository_password))
            client.set_options(wsse=auth)
        return client.service

    @Lazy
    def repository(self):
        return self._create_client('RepositoryService')

    @Lazy
    def navigation(self):
        return self._create_client('NavigationService')

    @Lazy
    def object(self):
        return self._create_client('ObjectService')

    @Lazy
    def discovery(self):
        return self._create_client('DiscoveryService')


class SOAPConnector(object):
    implements(ICMISConnector)

    def __init__(self, settings):
        self.have_object_not_found_exception = True
        self._settings = settings
        self._client = SOAPClient(settings)
        self._repository_id = None
        self._repository_info = None
        self._root = None

    @soap_error(object_lookup=True)
    @soap_cache
    def get_object_by_path(self, path, root=False):
        return properties_to_dict(
            self._client.object.getObjectByPath(
                repositoryId=self._repository_id,
                path=path,
                filter='*'),
            root=root)

    @soap_error()
    @soap_cache
    def get_object_by_cmis_id(self, cmis_id, root=False):
        return properties_to_dict(
            self._client.object.getObject(
                repositoryId=self._repository_id,
                objectId=cmis_id,
                filter='*'),
            root=root)

    @soap_error()
    @soap_cache
    def get_object_children(self, cmis_id):
        convert = lambda c: properties_to_dict(
            c.objectInFolder.object,
            identifier=getattr(c.objectInFolder, 'pathSegment', None))
        return map(convert, self._client.navigation.getDescendants(
                repositoryId=self._repository_id,
                folderId=cmis_id,
                depth=1,
                filter='*',
                includePathSegment=True))

    @soap_error()
    @soap_cache
    def get_object_parent(self, cmis_id):
        root_id = self._root['cmis:objectId']
        if cmis_id == root_id:
            return None, None
        parent = self._client.navigation.getObjectParents(
                repositoryId=self._repository_id,
                objectId=cmis_id,
                filter='*',
                includeRelativePathSegment=True)
        if not len(parent):
            return None, None
        return (properties_to_dict(parent[0].object, root=root_id),
                getattr(parent[0], 'relativePathSegment', None))

    def get_object_parents(self, cmis_id):
        parents = []
        current, identifier = self.get_object_parent(cmis_id)
        while current is not None:
            parents.append(current)
            cmis_id = current['cmis:objectId']
            parent, current_identifier = self.get_object_parent(cmis_id)
            if current_identifier:
                current['cmisbrowser:identifier'] = current_identifier
            current = parent
        return parents, identifier

    @soap_error()
    def query_for_objects(self, query, start=None, count=None):
        result = self._client.discovery.query(
            repositoryId=self._repository_id,
            statement=query,
            searchAllVersions=False)
        if result.numItems:
            return map(
                lambda c: properties_to_dict(c, prefix='R.'),
                result.objects)
        return []

    @soap_error()
    def get_object_content(self, cmis_id):

        def read_stream(stream):
            if isinstance(stream, suds.sax.text.Text):
                # If we have raw text, it is propably base64.
                return stream.decode('base64')
            return stream

        content = self._client.object.getContentStream(
            repositoryId=self._repository_id,
            objectId=cmis_id)
        return CMISFileResult(
            filename=content.filename,
            length=content.length,
            mimetype=content.mimeType,
            data=read_stream(content.stream))

    @soap_error()
    def start(self):
        if self._repository_id is not None:
            return self._root

        # Find repository id
        repositories = self._client.repository.getRepositories()
        if self._settings.repository_name:
            for repository in repositories:
                if self._settings.repository_name == repository.repositoryName:
                    break
            else:
                raise SOAPConnectorError(
                    u'Unknown repository: %s' % (
                        self._settings.repository_name))
        elif repositories is None:
            raise SOAPConnectorError(
                u"Cannot list available repositories.")
        elif len(repositories) == 1:
            repository = repositories[0]
        else:
            raise SOAPConnectorError(
                u'Multiple repository available. Please select one.')
        self._repository_id = repository.repositoryId
        self._repository_info = None
        # Find root
        if self._settings.repository_path:
            self._root = self.get_object_by_path(
                self._settings.repository_path,
                root=True)
        else:
            self._root = self.get_object_by_cmis_id(
                self.get_repository_info().rootFolderId,
                root=True)

        # Alfresco 3. doesn't return the proper exception for object
        # not found. Detect it and add it to the list.
        info = self.get_repository_info()
        if (info.productName.startswith('Alfresco') and
            info.productVersion[0] < '4'):
            self.have_object_not_found_exception = False
        return self._root

    @soap_error()
    def get_repository_info(self):
        if self._repository_info is None:
            self._repository_info = self._client.repository.getRepositoryInfo(
                self._repository_id)
        return self._repository_info

