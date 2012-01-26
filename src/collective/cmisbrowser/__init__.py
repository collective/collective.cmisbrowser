# this is a package.

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles("collective.cmisbrowser.AddCMISBrowser", ('Manager',))


def initialize(context):
    pass
