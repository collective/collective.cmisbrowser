# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

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

connector_source = SimpleVocabulary([
        SimpleTerm(
            value='soap',
            title=_('Connection SOAP')),
        SimpleTerm(
            value='rest',
            title=_('Connection REST'))])


class ICMISSettings(Interface):
    """Generic CMIS Settings.
    """
    title_from_plone = schema.Bool(
        title=_(u"Browser title comes Plone instead of CMIS repository"),
        description=_(u'Tell if the title of the browser should be the one set in Plone or of the root folder targeted in the CMIS repository.'),
        default=True,
        required=False)
    browser_description = schema.Text(
        title=_(u"Description"),
        required=False)
    browser_text = schema.Text(
        title=_(u"Text"),
        required=False)
    repository_url = schema.URI(
        title=_(u'CMIS repository URI'))
    repository_name = schema.TextLine(
        title=_(u'CMIS repository name'),
        description=_(u'If you have a federated CMIS repository, you have to type '
                      u'the name of the repository you want to access.'),
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
    repository_connector = schema.Choice(
        title=_('CMIS connection type to the repository'),
        description=_(u'Select if you want to connect to the CMIS repository using SOAP or REST.'),
        source=connector_source,
        default='soap',
        required=True)
    repository_cache = schema.Int(
        title=_('Time in minutes CMIS information should be cached'),
        min=0,
        default=5,
        required=True)
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

    Return object here are always simple directionaries containing the
    CMIS properties. Those are not Zope compatible objects. For those,
    refer to ICMISZopeAPI.

    This is an abstraction layer for REST and SOAP API.
    """

    def start():
        """Initialize the connector, and return a object representing
        the root object for this connector.
        """

    def get_object_by_path(path, root=False):
        """Return an object by its path, adjusting its type if it is a
        root.
        """

    def get_object_by_cmis_id(cmis_id, root=False):
        """Return an object by its id, adjusting its if it is a root.
        """

    def get_object_children(cmis_id):
        """Return a list of objects directly contained in the one
        specified by its id.
        """

    def get_object_parent(cmis_id):
        """Return a list of objects that are all parents of the one
        specified by its id. Stop at the root of the connector.
        """

    def query_for_objects(query, start=None, count=None):
        """Execute the given CMISQL query, and return the result as a
        list of objects.
        """

    def get_object_content(cmis_id):
        """Return an ICMISFileResult representing the data associated
        with the specified id. This is not applicable on non-fillable
        objects.
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

    def search(text, quotable=False, scorable=True):
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


class ICMISRootFolder(ICMISFolder):
    """A browsed root folder.
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
