# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.publisher.interfaces.browser import IBrowserPublisher
from plone.app.content.interfaces import INameFromTitle
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, Attribute
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


class CMISConnectorError(ValueError):

    def __init__(self, message, detail=None):
        ValueError.__init__(self, message, detail)
        self.message = message
        self.detail = detail

    def __str__(self):
        message = ': '.join((self.__class__.__name__, self.message))
        if self.detail:
            message = '\n'.join((message, self.detail))
        return message


class ICMISSettings(Interface):

    repository_url = schema.URI(
        title=_(u'CMIS repository URI'))
    repository_name = schema.TextLine(
        title=_(u'CMIS repository name'),
        required=False)
    repository_path = schema.TextLine(
        title=_(u'CMIS start folder path'),
        description=_(u'Folder in the CMIS repository at which the browser should start.'),
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


class ICMISConnector(Interface):
    """Connect to a CMIS repository.
    """


class ICMISContent(IBrowserPublisher):
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

    def Title():
        """Return content title.
        (Plone API).
        """

    def Description():
        """Return content description.
        (Plone API).
        """

    def CreationDate():
        """Return creation date as an ISO string (or 'None').
        (Plone API).
        """

    def ModificationDate():
        """Return modification date as an ISO string (or 'None').
        (Plone API).
        """

    def EffectiveDate():
        """Return effective date as an ISO string (or 'None').
        (Plone API).
        """

    def ExpirationDate():
        """Return expiration date as an ISO string (or 'None').
        (Plone API).
        """

    def Subject():
        """Return subjects as a tuple of strings.
        (Plone API).
        """

    def Type():
        """Return content type.
        (Plone API).
        """


class ICMISDocument(ICMISContent):
    """A content.
    """

    def CMISStreamId():
        """Return content CMIS stream identifier.
        """


class ICMISFolder(ICMISContent):
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


class ICMISBrowser(IBrowserPublisher, INameFromTitle, ICMISSettings):
    """A Browser.
    """

    def connect():
        """Return a connector to the current CMIS repository.
        """

    def getCMISBrowser():
        """Return self. (Use to get the browser by acquisition).
        """
