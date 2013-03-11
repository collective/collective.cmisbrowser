# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

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

    def __init__(self, filename, length, mimetype, stream=None, data=None):
        self.filename = filename
        self.length = length
        self.mimetype = mimetype
        self.stream = stream
        self.data = data

InitializeClass(CMISFileResult)
