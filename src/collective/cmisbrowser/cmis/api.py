# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging
import urllib

from Acquisition import aq_inner
from zExceptions import NotFound

from collective.cmisbrowser.cmis.content import CMISContent, CMISDocument
from collective.cmisbrowser.cmis.content import CMISFolder, CMISRootFolder
from collective.cmisbrowser.errors import CMISConnectorError
from collective.cmisbrowser.interfaces import ICMISFolder, ICMISConnector

logger = logging.getLogger('collective.cmisbrowser')


# This can be changed to a ZCML based registry for extensibility.
CMIS_FACTORIES = {
    'cmis:folder': CMISFolder,
    'cmis:document': CMISDocument,
    'default': CMISContent}


class CMISObjectAPI(object):

    def __init__(self, context):
        self.context = context
        self.connector = ICMISConnector(context)

        def create(properties, is_root=False):

            def get_factory():
                object_type = properties.get('cmis:objectTypeId')
                if object_type in CMIS_FACTORIES:
                    return CMIS_FACTORIES[object_type]
                base_type = properties.get('cmis:baseTypeId')
                if base_type in CMIS_FACTORIES:
                    return CMIS_FACTORIES[base_type]
                return CMIS_FACTORIES['default']

            factory = get_factory()
            if is_root:
                if not ICMISFolder.implementedBy(factory):
                    raise CMISConnectorError(
                        u'Connector root must be a folder in CMIS.')
                # Upgrade factory to root folder.
                factory = CMISRootFolder
            return factory(properties, self)

        self.root = self.connector.start(create).__of__(context)

    def traverse(self, name, content=None):
        if content is None:
            content = self.root
        path = content._properties.get('cmis:path')
        if path:
            path = '/'.join(
                (path.rstrip('/'),
                 urllib.unquote(name).decode('utf-8')))
            try:
                child = self.connector.get_object_by_path(path)
            except NotFound:
                # We ignore NotFound, to fallback on plone traversing.
                return None
            return child.__of__(aq_inner(content))
        return None

    def fetch(self, content):
        return self.connector.get_object_content(aq_inner(content)).__of__(content)

    def list(self, content):
        return map(
            lambda c: c.__of__(content),
            self.connector.get_object_children(content))
