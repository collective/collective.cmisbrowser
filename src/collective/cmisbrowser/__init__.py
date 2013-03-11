# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

# this is a package.



from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles("collective.cmisbrowser.AddCMISBrowser", ('Manager',))


def initialize(context):
    pass


@apply
def patch_plone():
    """We need to pactch security that is no properly declared in
    Plone 3.3, in order to be able to render templates when security
    is properly checked.
    """
    import pkg_resources

    packages = pkg_resources.working_set.resolve(
        [pkg_resources.Requirement.parse('Plone')])
    if len(packages):
        for package in packages:
            if package.project_name == 'Plone':
                if package.version < '4.0':
                    import plone.app.portlets.manager
                    import plone.app.contentmenu.view

                    plone.app.portlets.manager.ColumnPortletManagerRenderer.__allow_access_to_unprotected_subobjects__ = True
                    plone.app.contentmenu.view.ContentMenuProvider.__allow_access_to_unprotected_subobjects__ = True
                    return True
    return False

