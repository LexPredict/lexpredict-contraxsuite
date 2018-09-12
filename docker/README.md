# Contraxsuite: Quick Deployment

This folder contains scripts for fast deploying current 
latest Contraxsuite release on a clean Ubuntu 16.04 or 18.04 machine.

Contraxsuite application is provided as a Docker image
freely available at Docker Hub (https://hub.docker.com/r/lexpredict/lexpredict-contraxsuite/)
and a set of scripts and config files (this directory) allowing starting all components
required for Contraxsuite (including docker-compose.yml file).


## System Requirements
* Clean Ubuntu 16.04, 18.04 machine.
* At least 100GB free space on HDD at /.
* At least 16GB RAM.

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
Ensure that every service has at least 1 working container.
Docker Swarm cluster configuration (services, restrictions, e.t.c.) is in the docker-compose file specified
in setenv.sh (setenv_local.sh) in "DOCKER_COMPOSE_FILE" variable.
* After the installation is finished:
  * the Django-based UI of the Contraxsuite application will be available
at **http://localhost/advanced/**;
  * Jupyter having access to the Contraxsuite 
  python code and database will be at **http://localhost/jupyter/**;
  * Kibana connected to the Contraxsuite ElasticSearch will be at **http://localhost/kibana/**
    * Contraxsuite Django logs are in **logstash*** indexes
    * Documents indexed for search purposes are in **contraxsuite*** indexes. 

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

Contraxsuite Docker image maintains information about the last image version 
used on this deployment in contraxsuite_contraxsuite_deployment_uuid docker volume
(/var/lib/docker/volumes/contraxsuite_contraxsuite_deployment_uuid).
On each start Contraxsuite checks if the image is new by testing if 
stored uuid matches image uuid. For the case of new version Contraxsuite
re-installs theme and jqwidgets and runs Django collectstatic.

If during the installation or updating process some problems with CSS appear the following steps
can be used to force Contraxsuite re-installing the theme:
1. Undeploy the cluster using the script in docker/deploy.
2. Wait approx 15 seconds for it to finish.
3. Delete deployment uuid file from /var/lib/docker/volumes/contraxsuite_contraxsuite_deployment_uuid
4. Deploy the cluster again.

