# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Products.CMFDefault.permissions import View

try:
    # Support Zope 2.12+
    from App.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass

from zope.interface import implements

from collective.cmisbrowser.interfaces import ICMISStaleResult, ICMISFileResult


class CMISStaleResult(Implicit):
    """An unchanged file result from CMIS.
    """
    implements(ICMISStaleResult)
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self):
        pass

InitializeClass(CMISStaleResult)


class CMISFileResult(Implicit):
    """File content as download from CMIS.
    """
    implements(ICMISFileResult)
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self, filename, length, stream, mimetype):
        self.filename = filename
        self.length = length
        self.stream = stream
        self.mimetype = mimetype

InitializeClass(CMISFileResult)
