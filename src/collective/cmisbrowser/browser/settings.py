# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

from App.config import getConfiguration
from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel.form import ControlPanelForm
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.interface import implements, implementer

from collective.cmisbrowser.interfaces import ICMISSettings

_ = MessageFactory('collective.cmisbrowser')


class CMISSettings(ControlPanelForm):
    label = _("Site wide default settings for CMIS connections")
    description = _("Default settings used by every CMIS Browser in the site.")
    form_name = _("CMIS default settings")
    form_fields = form.Fields(ICMISSettings)
    form_fields['browser_text'].custom_widget = WYSIWYGWidget


class ConfigString(object):

    def __init__(self, name, is_unicode=False):
        self.name = name
        self.unicode = is_unicode

    def getter(prop, self):
        value = getattr(self._properties, prop.name, None)
        if not value:
            value = self._default.get(prop.name)
        if prop.unicode:
            return unicode(value)
        return value

    def setter(prop, self, value):
        if prop.unicode and isinstance(value, unicode):
            value = value.encode('utf-8')
        if value is None:
            # Plone properties doesn't support always None
            value = ''
        self._properties._updateProperty(prop.name, value)

    def property(prop):
        return property(prop.getter, prop.setter)


class ConfigInteger(ConfigString):

    def getter(prop, self):
        try:
            return int(super(ConfigInteger, prop).getter(self))
        except (TypeError, ValueError):
            return self._default.get(prop.name)


class ConfigBoolean(ConfigString):

    def getter(prop, self):
        try:
            return bool(super(ConfigBoolean, prop).getter(self))
        except (TypeError, ValueError):
            return self._default.get(prop.name)


class CMISSettingsAdapter(object):
    implements(ICMISSettings)

    def __init__(self, context):
        product_config = getattr(getConfiguration(), 'product_config', {})
        properties_tool = getToolByName(context, 'portal_properties')
        self._default = product_config.get('collective.cmisbrowser', {})
        self._properties = properties_tool.cmisbrowser_properties

    # Define overridable configuration entries.
    browser_description = ConfigString('browser_description', True).property()
    browser_text = ConfigString('browser_text', True).property()
    repository_url = ConfigString('repository_url').property()
    title_from_plone = ConfigBoolean('title_from_plone').property()
    repository_name = ConfigString('repository_name').property()
    repository_path = ConfigString('repository_path').property()
    repository_user = ConfigString('repository_user').property()
    repository_password = ConfigString('repository_password').property()
    repository_connector = ConfigString('repository_connector').property()
    repository_cache = ConfigInteger('repository_cache').property()
    folder_view = ConfigString('folder_view').property()
    proxy = ConfigString('proxy').property()


@implementer(ICMISSettings)
def default_cmis_settings(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    return ICMISSettings(portal)
