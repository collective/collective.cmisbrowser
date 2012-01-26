# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from collective.cmisbrowser.interfaces import ICMISBrowser
from plone.app.form.base import AddForm, EditForm
from zope.i18nmessageid import MessageFactory
from zope.component import createObject
from zope.formlib.form import applyChanges, Fields

_ = MessageFactory('collective.cmisbrowser')


class CMISBrowserAddForm(AddForm):
    label = _(u'Add a CMIS Browser')
    form_fields = Fields(ICMISBrowser)

    def create(self, data):
        browser = createObject(u"collective.cmisbrowser.CMISBrowser")
        applyChanges(browser, self.form_fields, data)
        return browser


class CMISBrowserEditForm(EditForm):
    label = _(u'Edit CMIS Browser')
    form_fields = Fields(ICMISBrowser)
