# Contraxsuite Third-party Dependencies Folder

This folder is for licensed third-party dependencies of the Contraxsuite platform.

Please put the following files here before running Contraxsuite Docker Image deployment scripts:
* jqwidgets-example.zip - zipped JQWidgets Library
  * jqwidgets
    * globalization
    * styles
    * jqx-all.js
    * ...
* theme-example.zip - zipped theme
  * Package-HTML
    * HTML
      * css
      * images
      * js
      * style.css


deploy-contraxsuite-to-swarm-cluster.sh script will first unzip the depedencies to the Docked volume dir and next deploy Contraxsuit Docker images so that they will use the volumes.