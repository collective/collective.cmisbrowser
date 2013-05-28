======================
collective.cmisbrowser
======================

.. contents::

Presentation
============

collective.cmisbrowser is a Plone 3.2+ extension that lets you connect to
a `CMIS`_ document repository and browse its content from Plone.

It provides a content type called *CMIS Browser* that after being added
lets you browse the content of the repository like if it was Plone
content (modulo the fact that it is not).

Installation
============

Update buildout profile
-----------------------

Update your buildout profile to include the following eggs and zcml::

  eggs +=
      ...
      collective.cmisbrowser
  zcml +=
      ...
      collective.cmisbrowser

**Important:**

When using python 2.4.x you will also need to add *httpsproxy_urllib2*
as an egg.

Run the buildout
----------------

Run the buildout to reflect the changes you made to the profile::

  $ bin/buildout -v

Install the extension
---------------------

The extension can be installed through the ZMI or Plone control panel.

Through the ZMI
~~~~~~~~~~~~~~~

 - Go to the *portal quickinstaller* in the ZMI.

 - Check the extension *collective.cmisbrowser*.

 - Click the *install* button.

Through the Plone control panel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - Go to *Site Setup*.

 - Choose *Add-on products*.

 - Check the extension *collective.cmisbrowser*.

 - Click the *Install* button.

Add a CMIS Browser
==================

After installing you will be able to add a *CMIS Browser* in your Plone
site from the *Add new...* drop-down menu. Configuration can be done on
the *CMIS Browser* itself and/or you can set a site wide configuration.

Configuration
=============

The side wide configuration can be set in the *CMIS settings* in the
*Add-on Product Configuration* section of *Site Setup*. Non site wide
configuration can be set on the *CMIS Browser*.

CMIS Browser
------------

A *CMIS Browser* provides the following options:

- ``browser_description``: A description of the browser.

- ``browser_text``: Additional WYSIWYG text field for the browser.

- ``repository_url``: URL to the connected `CMIS`_ repository.

- ``title_from_plone``: Use the title from Plone and not the one from
  the repository.

- ``repository_name``: Name of the repository to use at the connected
  URL. Required if more than one repository is available.

- ``repository_path``: Path in the repository to use as root for the
  Browser. If it is not specified, the root of the repository will be
  used.

- ``repository_user``: Username used to authenticate to the
  repository. If specified, password is required.

- ``repository_password``: Password used to authenticate to the
  repository. If specified, username is required.

- ``repository_connector``: The type of connection that needs to be used
  SOAP or REST.

- ``repository_cache``: How long the CMIS content should be cached.

- ``folder_view``: Choice that lets you choose how CMIS folders are
  rendered in Plone. This let you select which Plone folder template
  to use.

- ``proxy``: Proxy URL to use to connect to the CMIS repository.

In the Plone control panel, you have access to a *CMIS settings*
control panel. It lets you define default settings to use for all newly
created *CMIS Browser*. Those defaults are stored in the Plone
properties, and are easily exportable with the help of GenericSetup.

As well, you can provide Zope defaults in the Zope configuration file,
``zope.conf``::

   <product-config collective.cmisbrowser>
       repository_url http://orange:8080/alfresco/cmis
       repository_user admin
       repository_password admin
   </product-config>


This can be added into ``zope.conf`` by buildout, with the help of the
directive ```zope-conf-additional`` of `plone.recipe.zope2instance`_.

Configure RAM Cache
-------------------

Go to: http://[plone–site]/ramcache–controlpanel

RAM Cache Statistics
~~~~~~~~~~~~~~~~~~~~

Gives an overview of the cached items.

Clear RAM cache
~~~~~~~~~~~~~~~

Click on the *Clear cache* button to clear all cached content.

RAM Cache Settings
~~~~~~~~~~~~~~~~~~

This configuration overview gives you the possibility to alter the
default values of the following parameters:

 - A maximum number of cached values.

 - Maximum age for cached values in seconds.

 - An interval between cache cleanups in seconds.

Change the values and click the *Save* button.

Compatibility
=============

This product has been tested with `Alfresco`_, but is intended to be
generic and usable with any `CMIS`_ content repository.

.. _plone.recipe.zope2instance: http://pypi.python.org/pypi/plone.recipe.zope2instance
.. _Alfresco: http://www.alfresco.com/community/
.. _CMIS: http://docs.oasis-open.org/cmis/CMIS/v1.0/cs01/cmis-spec-v1.0.html
