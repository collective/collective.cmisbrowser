# Copyright (c) 2012 Vlaamse Overheid. All rights reserved.
# See also LICENSE.txt

# this is a package.

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles("collective.cmisbrowser.AddCMISBrowser", ('Manager',))


def initialize(context):
    pass
