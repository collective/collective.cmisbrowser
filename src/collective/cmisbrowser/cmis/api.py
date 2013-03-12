# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

import logging
import urllib
import re

from Acquisition import aq_inner
from zExceptions import NotFound
from zope.component import getAdapter
from zope.interface import implements

from collective.cmisbrowser.cmis.content import CMISContent, CMISDocument
from collective.cmisbrowser.cmis.content import CMISFolder, CMISRootFolder
from collective.cmisbrowser.interfaces import ICMISConnector
from collective.cmisbrowser.interfaces import ICMISZopeAPI

logger = logging.getLogger('collective.cmisbrowser')


def quote(text):

    def escape(x):
        if x.group(0) == "'":
            return "\\'"
        return x.group(0)

    return re.sub(r"""(\\.|.)""", escape, text)


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
        self.connector = getAdapter(context, ICMISConnector, name=context.repository_connector)
        self.root = self._build(
            parent=self.context,
            content=self.connector.start())

    def info(self):
        return self.connector.get_repository_info()

    def _build(self, parent=None, content=None, contents=[]):
        if parent is not None:
            parent = aq_inner(parent)
            get_parent = lambda properties: parent
        else:

            def get_parent(properties):
                context = self.context
                parents, identifier = self.connector.get_object_parents(
                    properties['cmis:objectId'])
                if identifier:
                    properties['cmisbrowser:identifier'] = identifier
                for ancestor in reversed(parents):
                    context = get_cmis_factory(ancestor)(
                        ancestor, self).__of__(context)
                return context

        def build(properties):
            parent = get_parent(properties)
            factory = get_cmis_factory(properties)
            return factory(properties, self).__of__(parent)

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

    def query(self, query):
        results = self.connector.query_for_objects(query)
        return self._build(parent=None, contents=results)

    def search(self, text, quotable=False, scorable=True):
        if not text:
            # No text, return an empty list.
            return []
        if quotable:
            text = quote(text)
        elif "'" in text:
            # By default you can't quote quotes in CMIS. Only Alfresco support it.
            return []
        if scorable:
            query = u"SELECT R.*, SCORE() as TEXT_SCORE FROM cmis:document R " + \
                u"WHERE CONTAINS('%s') AND IN_TREE(R, '%s') ORDER BY TEXT_SCORE DESC" % (
                text,
                self.root.CMISId())
        else:
            query = u"SELECT R.*  FROM cmis:document R " + \
                u"WHERE CONTAINS('%s') AND IN_TREE(R, '%s')" % (
                text,
                self.root.CMISId())
        return self.query(query)
