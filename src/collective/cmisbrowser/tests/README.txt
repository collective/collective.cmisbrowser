
You can configure the CMIS repository to use in order to run the test
with the help of environment variables:

  #!/usr/bin/env bash
  export CMIS_REPOSITORY_URL_SOAP='http://orange.infrae:8080/alfresco/cmis'
  export CMIS_REPOSITORY_URL_REST='http://orange.infrae:8080/alfresco/s/cmis'
  export CMIS_REPOSITORY_USER='admin'
  export CMIS_REPOSITORY_PASSWORD='admin'
  bin/test

A test folder called 'testfolder' will be create at the root of the
repository, and some test content will be imported in it, using the
REST API.
