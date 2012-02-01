# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import collective.cmisbrowser
    zcml.load_config('configure.zcml', collective.cmisbrowser)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.cmisbrowser')


setup_product()
ptc.setupPloneSite(products=['collective.cmisbrowser'])

class CMISBrowserTestCase(ptc.PloneTestCase):
    pass

