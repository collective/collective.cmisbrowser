# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Acquisition import aq_inner
from Products.Five.browser import BrowserView


class CMISFolderView(BrowserView):

    def __call__(self):
        # Render the Plone folder view selected in the browser.
        browser = self.context.getCMISBrowser()
        view = getattr(aq_inner(self.context), browser.folder_view)
        return view()


class CMISBrowserView(BrowserView):
    pass
