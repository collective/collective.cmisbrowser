# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

from Acquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from zope.component import getMultiAdapter
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.interface import implements


class AbsoluteURL(BrowserView):
    implements(IAbsoluteURL)
    # For ICMISContent

    def __str__(self):
        return aq_inner(self.context).absolute_url()

    __call__ = __str__
    __unicode__ = __str__
    __repr__ = __str__

    def breadcrumbs(self):
        context = aq_inner(self.context)
        container = aq_parent(context)
        result = getMultiAdapter((container, self.request), IAbsoluteURL).breadcrumbs()

        identifier = context.getId()
        if identifier is not None:
            return tuple(result) + (
                {'name': context.Title(),
                 'url': "/".join((result[-1]['url'], identifier,))},)
        return result


class NavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = aq_inner(self.context)
        container = aq_parent(context)
        result = getMultiAdapter((container, self.request), name="breadcrumbs_view").breadcrumbs()

        identifier = context.getId()
        if identifier is not None:
            return tuple(result) + (
                {'Title': context.Title(),
                 'absolute_url': "/".join((result[-1]['absolute_url'], identifier,))},)
        return result
