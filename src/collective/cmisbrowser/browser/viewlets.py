# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

from plone.app.layout.viewlets import common as base


class TextViewlet(base.ViewletBase):

    def render(self):
        body = self.context.getBody()
        if body:
            return body
        return u''
