# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from App.config import getConfiguration
from Products.CMFCore.utils import getToolByName
from plone.app.controlpanel.form import ControlPanelForm
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from collective.cmisbrowser.interfaces import ICMISSettings

_ = MessageFactory('collective.cmisbrowser')


class CMISSettings(ControlPanelForm):
    label = _("Site wide default settings for CMIS connections")
    description = _("Default settings used by every CMIS Browser in the site.")
    form_name = _("CMIS default settings")
    form_fields = form.Fields(ICMISSettings)


def configurable_string(name):

    def getter(self):
        value = getattr(self._properties, name, None)
        if not value:
            return self._default.get(name)
        return value

    def setter(self, value):
        if value is None:
            # Plone properties doesn't support always None
            value = ''
        self._properties._updateProperty(name, value)

    return property(getter, setter)


class CMISSettingsAdapter(object):
    implements(ICMISSettings)

    def __init__(self, context):
        product_config = getattr(getConfiguration(), 'product_config', {})
        properties_tool = getToolByName(context, 'portal_properties')
        self._default = product_config.get('collective.cmisbrowser', {})
        self._properties = properties_tool.cmisbrowser_properties

    # Define overridable configuration entries.
    repository_url = configurable_string('repository_url')
    repository_name = configurable_string('repository_name')
    repository_path = configurable_string('repository_path')
    repository_user = configurable_string('repository_user')
    repository_password = configurable_string('repository_password')
    folder_view = configurable_string('folder_view')
    proxy = configurable_string('proxy')
