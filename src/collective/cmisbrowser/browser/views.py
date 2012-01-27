# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Five.browser import BrowserView


class CMISFolderBrowser(BrowserView):

    def __call__(self):
        return self.context.aq_inner.folder_tabular_view()
