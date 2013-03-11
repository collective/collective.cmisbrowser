# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

from Products.CMFCore.utils import getToolByName

from plone.app.layout.icons.icons import BaseIcon
from plone.app.layout.icons.interfaces import IContentIcon
from zope.interface import implements


class CMISContentIcon(BaseIcon):
    implements(IContentIcon)
    width = 16
    height = 16

    def __init__(self, context, request, content):
        self.context = context
        self.request = request
        self.content = content

    @property
    def title(self):
        return None

    @property
    def description(self):
        return self.content.portal_type

    @property
    def url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        return "/".join((portal_url, self.content.portal_icon))
