# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import suds
import subprocess
import urllib2

from collective.cmisbrowser.interfaces import ICMISConnector, CMISConnectorError
from collective.cmisbrowser.cmis.result import CMISFileResult
from zope.interface import implements
from zope.cachedescriptors.property import CachedProperty

from zExceptions import NotFound


def indent_xml(xml):
    # This is used for debug.
    stdout, stderr = subprocess.Popen(
        'xmlindent', stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate(
        input=xml)
    return stdout


class SOAPConnectorError(CMISConnectorError):
    pass



def soap_error(wrapped):

    def wrapper(self, *args, **kwargs):
        try:
            return wrapped(self, *args, **kwargs)
        except urllib2.URLError, error:
            raise SOAPConnectorError(
                u'Network transport error: %s' % error.args[0][1])
        except suds.transport.TransportError, error:
            raise SOAPConnectorError(
                u'HTTP transport error, code %d' % error.httpcode,
                indent_xml(error.fp.read()))
        except suds.WebFault, error:
            cmis_error = getattr(error.fault.detail, 'cmisFault', None)
            if cmis_error is not None:
                # In case of object not found, we convert to a Zope error
                if cmis_error.type == 'objectNotFound':
                    raise NotFound()
            raise SOAPConnectorError(
                error.fault.faultstring,
                error.document.str())

    return wrapper


def properties_to_dict(properties):
    values = []
    entry = properties.__dict__

    def serialize(value):
        if len(value.value):
            assert len(value.value) == 1, 'not supported'
            values.append(
                (value._propertyDefinitionId,
                 value.value[0]))

    for key in entry.keys():
        if not key.startswith('property'):
            continue
        value = entry.get(key, [])
        if isinstance(value, list):
            map(serialize, value)
        else:
            serialize(value)
    return dict(values)


class SOAPClient(object):

    def __init__(self, settings):
        self.settings = settings

    def _create_client(self, service):
        """Create an authenticated SOAP client to access an SOAP
        service.
        """
        client = suds.client.Client(
            '/'.join((self.settings.repository_url, service)) + '?wsdl')
        if self.settings.repository_user:
            if self.settings.repository_password is None:
                raise SOAPConnectorError(
                    u'Settings specify user and not password.')
            auth = suds.wsse.Security()
            # Timestamp must be included, and be first for alfresco.
            auth.tokens.append(suds.wsse.Timestamp())
            auth.tokens.append(suds.wsse.UsernameToken(
                    self.settings.repository_user,
                    self.settings.repository_password))
            client.set_options(wsse=auth)
        if self.settings.proxy:
            client.set_options(proxy={'http': self.settings.proxy,
                                      'https': self.settings.proxy})
        return client.service

    @CachedProperty
    def repository(self):
        return self._create_client('RepositoryService')

    @CachedProperty
    def navigation(self):
        return self._create_client('NavigationService')

    @CachedProperty
    def object(self):
        return self._create_client('ObjectService')



class SOAPConnector(object):
    implements(ICMISConnector)

    def __init__(self, settings):
        self._settings = settings
        self._client = SOAPClient(settings)
        self._repository_id = None
        self._repository_info = None
        self._root_id = None
        self._factory = None

    def _create(self, result, is_root=False):
        assert self._factory is not None
        return self._factory(
            properties_to_dict(result.properties),
            is_root=is_root)

    @soap_error
    def get_object_by_path(self, path, is_root=False):
        return self._create(
            self._client.object.getObjectByPath(
                repositoryId=self._repository_id,
                path=path,
                filter='*'),
            is_root=is_root)

    @soap_error
    def get_object_by_cmis_id(self, cmis_id, is_root=False):
        return self._create(
            self._client.object.getObject(
                repositoryId=self._repository_id,
                objectId=cmis_id,
                filter='*'),
            is_root=is_root)

    @soap_error
    def get_object_children(self, cmis_object):
        create = lambda c: self._create(c.objectInFolder.object)
        return map(create, self._client.navigation.getDescendants(
                repositoryId=self._repository_id,
                folderId=cmis_object.CMISId(),
                depth=1,
                filter='*'))

    @soap_error
    def get_object_content(self, cmis_object):
        content = self._client.object.getContentStream(
            repositoryId=self._repository_id,
            objectId=cmis_object.CMISId())
        return CMISFileResult(
            filename=content.filename,
            length=content.length,
            stream=content.stream,
            mimetype=content.mimeType)

    @soap_error
    def start(self, factory):
        if self._repository_id is not None:
            return
        # We can't get factory as a parameter in __init_,
        # because we are an adapter.
        self._factory = factory

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
                is_root=True)
        else:
            self._root = self.get_object_by_cmis_id(
                self.get_repository_info().rootFolderId,
                is_root=True)
        return self._root

    @soap_error
    def get_repository_info(self):
        if self._repository_info is None:
            self._repository_info = self._client.repository.getRepositoryInfo(
                self._repository_id)
        return self._repository_info

