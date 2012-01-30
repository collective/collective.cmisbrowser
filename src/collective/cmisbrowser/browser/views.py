# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from zope.datetime import rfc1123_date


class CMISFileResultView(BrowserView):
    """Return a file result, with correct headers.
    """

    def __call__(self):
        # Download the asset.
        response = self.request.response
        response.setHeader(
            'Content-Disposition',
            'inline;filename=%s' % self.context.filename)
        response.setHeader(
            'Content-Length',
            '%s' % self.context.length)
        response.setHeader(
            'Content-Type',
            self.context.mimetype)
        # For caching, acquired one level.
        response.setHeader(
            'Last-Modified',
            rfc1123_date(self.context.modified()))
        # We don't support advanced streaming (yet).
        response.setHeader(
            'Accept-Ranges', None)
        return self.context.stream


class CMISStaleResultView(BrowserView):
    """Mark the result as not changed.
    """

    def __call__(self):
        response = self.request.response
        response.setStatus(304)
        return u''


class CMISFolderView(BrowserView):
    """Render the corresponding folder view.
    """

    def __call__(self):
        # Render the Plone folder view selected in the browser.
        browser = self.context.getCMISBrowser()
        view = getattr(aq_inner(self.context), browser.folder_view)
        return view()


class CMISBrowserView(BrowserView):

    def __call__(self):
        # This is an error page, we don't want to cache it
        response = self.request.response
        response.setStatus(502)
        response.setHeader(
            'Cache-Control',
            'no-cache, must-revalidate, post-check=0, pre-check=0')
        response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
        response.setHeader('Pragma', 'no-cache')
        return self.index()
