======================
collective.cmisbrowser
======================

.. contents::

Presentation
============

collective.cmisbrowser is a Plone 3.2+ extension that let you connect to
a `CMIS`_ document repository and browse its content from Plone.

It provides a content type, a *CMIS Browser* that after added let your
browse the content of the repository like if it was Plone content
(modulo the fact that it is not).

Configuration
=============

A *CMIS Browser* provide you with the following options:

- ``repository_url``: URL to the connected `CMIS`_ repository,

- ``repository_name``: Name of the repository to use at the connected
  URL (if more than one is available),

- ``repository_path``: Sub path in the repository to start browsing at,

- ``repository_user``: Username used to authenticate to the repository,

- ``repository_password``: Password used to authenticate to the repository,

- ``folder_view``: Choice that let select how CMIS folders are
  rendered in Plone. This let you select which Plone folder default
  template to use.

- ``proxy``: Proxy URL to use to connect to the CMIS repository.

In the Plone control panel, you have access to a *CMIS settings*
control panel. It let you define default settings to use for all newly
created *CMIS Browser*. Those default are stored in the Plone
properties, and are easily exportable with the help of GenericSetup.

As well, you can provide Zope default in the Zope configuration file,
``zope.conf``::

   <product-config collective.cmisbrowser>
       repository_url http://orange:8080/alfresco/cmis
       repository_user admin
       repository_password admin
   </product-config>


This can be added into ``zope.conf`` by buildout, with the help of the
directive ```zope-conf-additional`` of `plone.recipe.zope2instance`_.

Compatibility
=============

This product have been tested with `Alfresco`_, but is intended to be
generic and usable with any `CMIS`_ content repository.

.. _plone.recipe.zope2instance: http://pypi.python.org/pypi/plone.recipe.zope2instance
.. _Alfresco: http://www.alfresco.com/community/
.. _CMIS: http://docs.oasis-open.org/cmis/CMIS/v1.0/cs01/cmis-spec-v1.0.html
