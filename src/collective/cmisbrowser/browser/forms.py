# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

from plone.app.content.interfaces import INameFromTitle
from plone.app.form.base import AddForm, EditForm
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from zope.component import createObject
from zope.formlib.form import applyChanges, Fields, setUpEditWidgets
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from collective.cmisbrowser.interfaces import ICMISSettings, IRSSSetting

_ = MessageFactory('collective.cmisbrowser')


class CMISBrowserAddForm(AddForm):
    label = _(u'Add a CMIS Browser')
    form_fields = Fields(INameFromTitle, ICMISSettings)
    form_fields['browser_text'].custom_widget = WYSIWYGWidget

    def setUpWidgets(self, ignore_request=False):
        # We setup the add form like an edit form, in order to read
        # the default values provided in the settings.
        self.adapters = {}
        self.widgets = setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request)

    def create(self, data):
        browser = createObject(u"collective.cmisbrowser.CMISBrowser")
        applyChanges(browser, self.form_fields, data)
        return browser


class CMISBrowserEditForm(EditForm):
    label = _(u'Edit CMIS Browser')
    form_fields = Fields(INameFromTitle, ICMISSettings, IRSSSetting)
    form_fields['browser_text'].custom_widget = WYSIWYGWidget


# The default title adapter is used by the add form
class DefaultTitleAdapter(object):
    implements(INameFromTitle)

    def __init__(self, context):
        self.title = None


class RSSSettingAdapter(object):
    implements(IRSSSetting)

    def __init__(self, context):
        self.context = aq_inner(context)
        self.tool = getToolByName(context, 'portal_syndication')

    @apply
    def folder_rss():

        def getter(self):
            return bool(self.tool.isSyndicationAllowed(self.context))

        def setter(self, value):
            is_enabled = getter(self)
            if is_enabled != value:
                if value:
                    self.tool.enableSyndication(self.context)
                else:
                    self.tool.disableSyndication(self.context)

        return property(getter, setter)
