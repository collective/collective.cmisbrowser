# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging
import urllib

from Acquisition import aq_inner
from zExceptions import NotFound
from zope.interface import implements

from collective.cmisbrowser.cmis.content import CMISContent, CMISDocument
from collective.cmisbrowser.cmis.content import CMISFolder, CMISRootFolder
from collective.cmisbrowser.interfaces import ICMISConnector
from collective.cmisbrowser.interfaces import ICMISZopeAPI

logger = logging.getLogger('collective.cmisbrowser')


# This can be changed to a ZCML based registry for extensibility.
# cmisbrowser:root is an alias for the connection root folder.
CMIS_FACTORIES = {
    'cmisbrowser:root': CMISRootFolder,
    'cmis:folder': CMISFolder,
    'cmis:document': CMISDocument,
    'default': CMISContent}


def get_cmis_factory(properties):
    object_type = properties.get('cmis:objectTypeId')
    if object_type in CMIS_FACTORIES:
        return CMIS_FACTORIES[object_type]
    base_type = properties.get('cmis:baseTypeId')
    if base_type in CMIS_FACTORIES:
        return CMIS_FACTORIES[base_type]
    return CMIS_FACTORIES['default']


class CMISZopeAPI(object):
    implements(ICMISZopeAPI)

    def __init__(self, context):
        self.context = context
        self.connector = ICMISConnector(context)
        self.root = self._build(
            parent=self.context,
            content=self.connector.start())

    def _build(self, parent=None, content=None, contents=[]):
        if parent is not None:
            parent = aq_inner(parent)
            get_parent = lambda properties: parent
        else:

            def get_parent(properties):
                parent = self.context
                for ancestor in reversed(
                    self.connector.get_object_parents(
                        properties['cmis:objectId'])):
                    parent = get_cmis_factory(ancestor)(
                        ancestor, self).__of__(parent)
                return parent

        def build(properties):
            factory = get_cmis_factory(properties)
            return factory(properties, self).__of__(get_parent(properties))

        if content is not None:
            return build(content)
        return map(build, contents)

    def traverse(self, name, context=None):
        if context is None:
            context = self.root
        path = context._properties.get('cmis:path')
        if path:
            path = '/'.join(
                (path.rstrip('/'),
                 urllib.unquote(name).decode('utf-8')))
            try:
                child = self.connector.get_object_by_path(path)
            except NotFound:
                # We ignore NotFound, to fallback on plone traversing.
                return None
            return self._build(parent=context, content=child)
        return None

    def fetch(self, content):
        return self.connector.get_object_content(content.CMISId()).__of__(content)

    def list(self, container):
        return self._build(
            parent=container,
            contents=self.connector.get_object_children(container.CMISId()))

    def search(self, text):
        escaped_text = "'%s'" % text.replace("'", "\'")
        return self._build(
            parent=None,
            contents=self.connector.query_for_objects(
                "SELECT R.*, SCORE() AS SEARCH_SCORE FROM cmis:document R "
                "WHERE CONTAINS(%s) AND IN_TREE(R, '%s') ORDER BY SEARCH_SCORE DESC" % (
                    escaped_text, self.root.CMISId())))
