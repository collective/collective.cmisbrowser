# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from plone.app.content.interfaces import INameFromTitle
from plone.app.form.base import AddForm, EditForm
from zope.component import createObject
from zope.formlib.form import applyChanges, Fields, setUpEditWidgets
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from collective.cmisbrowser.interfaces import ICMISBrowser

_ = MessageFactory('collective.cmisbrowser')


class CMISBrowserAddForm(AddForm):
    label = _(u'Add a CMIS Browser')
    form_fields = Fields(ICMISBrowser)

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
    form_fields = Fields(ICMISBrowser)


# The default title adapter is used by the add form
class DefaultTitleAdapter(object):
    implements(INameFromTitle)

    def __init__(self, context):
        self.title = None
