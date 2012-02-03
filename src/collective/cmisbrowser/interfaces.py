# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.CMFPlone.interfaces.constrains import IConstrainTypes
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFCore.interfaces import IDublinCore

from plone.app.content.interfaces import INameFromTitle
from zope import schema
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, Attribute, invariant, Invalid
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

_ = MessageFactory('collective.cmisbrowser')
_plone = MessageFactory('plone')


folder_view_source = SimpleVocabulary([
        SimpleTerm(
            value='folder_listing',
            title=_plone('Standard view')),
        SimpleTerm(
            value='folder_summary_view',
            title=_plone('Summary view')),
        SimpleTerm(
            value='folder_tabular_view',
            title=_plone('Tabular view'))])



class ICMISSettings(Interface):
    """Generic CMIS Settings.
    """
    repository_url = schema.URI(
        title=_(u'CMIS repository URI'))
    repository_name = schema.TextLine(
        title=_(u'CMIS repository name'),
        required=False)
    repository_path = schema.TextLine(
        title=_(u'CMIS start folder path'),
        description=_(u'Folder in the CMIS repository at which the browser should start, '
                      u'will start at the root of the repository if this is empty.'),
        required=False)
    repository_user = schema.TextLine(
        title=_(u'User to access CMIS repository'),
        required=False)
    repository_password = schema.Password(
        title=_(u'Password to access CMIS repository'),
        required=False)
    folder_view = schema.Choice(
        title=_(u'Plone template used to render folders'),
        description=_(u'Select a default plone template to render folders.'),
        default='folder_listing',
        source=folder_view_source,
        required=True)
    proxy = schema.URI(
        title=_(u'HTTP-Proxy to use to access CMIS repository'),
        required=False)

    @invariant
    def validate_user_and_password(data):
        if data.repository_user and not data.repository_password:
            raise Invalid(_(u'Username specified, but password missing.'))
        if data.repository_password and not data.repository_user:
            raise Invalid(_(u'Password specified, but username missing.'))

    def UID():
        """return an unique identifier for those settings.
        """


class IRSSSetting(Interface):
    """Enable RSS setting.
    """
    folder_rss = schema.Bool(
        title=_(u'Enable RSS feed'),
        description=_(u'If this is checked, an RSS feed will be available on every CMIS folder.'),
        required=True)


class ICMISConnector(Interface):
    """Connect to a CMIS repository.
    """


class ICMISZopeAPI(Interface):
    """High level API to talk to CMIS that returns Zope aware objects.
    """
    context = Attribute(u"Context at which the CMIS connection starts")
    connector = Attribute(u"Low level API")
    root = Attribute(u"CMIS object considered as root by this API")

    def traverse(name, context=None):
        """Traverse to a sub object called name, starting from root,
        or from content is specified.
        """

    def fetch(content):
        """Fetch the data stream associated with the content. This
        return a ICMISFileResult.
        """

    def list(container):
        """Return as a list all the CMIS content contained in the
        given container one.
        """

    def search(text):
        """Search all CMIS content that contains the given text.
        """


class ICMISContent(IBrowserPublisher, IDublinCore):
    """A browsed document.
    """
    portal_type = Attribute(u"Portal content name to be displayed")
    portal_icon = Attribute(u"Icon to be used")

    def getId():
        """Return content identifier in Zope.
        (Zope API)
        """

    def CMISId():
        """Return content CMIS identifier.
        """

    def getCMISBrowser():
        """Return associated browser object.
        """


class ICMISDocument(ICMISContent):
    """A content.
    """


class ICMISFolder(ICMISContent, INonStructuralFolder):
    """A browsed folder.
    """

    def getFolderContents():
        """Return folder content as a list (or batch) of
        ICMISDocument. Please refer to the plone script for more
        detail.
        (Plone API).
        """


class ICMISStaleResult(Interface):
    """Represent an unmodified result from CMIS.
    """


class ICMISFileResult(Interface):
    """Represent file data download from CMIS.
    """
    filename = Attribute('filename')
    length = Attribute('length')
    stream = Attribute('stream')
    mimetype = Attribute('mimetype')


class ICMISBrowser(IBrowserPublisher, INonStructuralFolder,
                   INameFromTitle, IConstrainTypes,
                   IAttributeAnnotatable, ICMISSettings):
    """A Browser.
    """
