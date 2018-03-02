# Contraxsuite: Quick Deployment

This folder contains scripts for fast deploying current 
latest Contraxsuite release on a clean Ubuntu 16.04 machine.

Contraxsuite application is provided as a Docker image
freely available at Docker Hub (https://hub.docker.com/r/lexpredict/lexpredict-contraxsuite/)
and a set of scripts and config files (this directory) allowing starting all components
required for Contraxsuite (including docker-compose.yml file).


## System Requirements
* Clean Ubuntu 16.04 (or later - not tested) machine.
* At least 16GB free space on HDD at /.
* At least 8GB RAM.

## Installation
* Unpload/unpack all files of this dir to the machine.
* Put zipped theme and jqwidgets files into ./deploy/dependencies directory.
  
  Contents of ./deploy/dependencies should be similar to this:
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
      
* Run script: **setup_local_contraxsuite_ubuntu_16_04.sh**

  The script will execute the following actions:
  * install Docker, 
  * initialize Docker Swarm cluster consisting of this single machine, 
  * download the latest Contraxsuite Docker image from Docker Hub, 
  * deploy services configured in ./deploy/docker-compose.yml file.
  
* Wait few minutes for all components to start (sudo docker service ls).
  
* After the installation is finished the Contraxsuite application will be available 
at **http://localhost:65080**. 

  Admin login/pass: Administrator/Administrator.
  
## Updating to the Latest Contraxsuite Image
To update running Contraxsuite demo application installed by these scripts to
to the latest version you can run the following script on the machine: 
**update_local_contraxsuite_to_latest_version.sh**

Database and documents uploaded to the system will be preserved after update.

## Advanced Usage
These scripts can be used to run Contraxsuite in a distributed Docker Swarm cluster
consisting of multiple machines.

Check ./deploy/new_contraxsuite_cluster_ubuntu_16_04.sh for more info.

For more complicated deployments and support please contact LexPredict team. 
