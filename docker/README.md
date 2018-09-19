# Contraxsuite: Quick Deployment

This folder contains scripts for deploying the current 
latest Contraxsuite release on a clean Ubuntu 16.04 or 18.04 machine.

## Architecture

Contraxsuite is a Python/Django based application.

Contraxsuite deployment consists of the following main components:
* Django Web application (UWSGI) - Django-based UI, REST API
* Postgres - main database
* Celery Beat Scheduler - periodical tasks scheduling
* Celery Workers (1 or more) - asynchronous task processing
* RabbitMQ - message queue for Celery
* Flower - Celery management UI
* Jupyter - Jupyter Notebook application connected to the Contraxsuite code and DB for experimenting
* Elasticsearch - full text search, log storage
* Tika REST Servers (1 or more) - text extraction from different file formats
* Filebeat - logs collecting
* Metricbeat - metrics collecting
* Kibana - web UI for accessing Elasticsearch data, logs, metrics
* Nginx - web server and reverse proxy server routing request among the web backends, HTTPS support

To simplify the deployment and management of these components the Contraxsuite platform uses Docker Swarm 
clustering platform.

Main Contraxsuite Python project tree and scripts for starting Django and Celery is distributed 
as a Docker image freely available at Docker-Hub (https://hub.docker.com/r/lexpredict/lexpredict-contraxsuite/).
The same Docker image is used for starting: Django, Celery Beat and Celery Worker containers.

To wire all components together the Docker Swarm uses docker-compose.yml config files.
Contraxsuite can be scaled onto different deployment architectures depending on the concrete needs of
the user. 
For example docker-compose.yml files are provided for the following architectures:
* Single-host deployment.
    * Requires only one server. 
    * Suitable for learning the system.
    * Processes documents slower than multi-server deployments.
* Single master, many workers.
    * (1) One bigger server for Web server, DB and other components, (2) any number of Celery workers for data processing.
    * The most stable and standard architecture. 
    * Works good for big number of documents.
    * Celery workers can be put into auto-scaling groups at AWS which will grow/decrease depending on the current load.
* Two masters, many workers
    * (1) One server for DB; (2) One server for web server, and other components, (3) any number of Celery workers
    * Used for splitting CPU/memory resources between DB and Web server components.
    * Mostly used for debugging/testing under the big load.
* Two masters, many workers with only primary components enabled.
    * The same as previous but with logging, filebeat, metricbeat, flower and other not very important 
    components turned off.
    * Used for debugging/testing under the big load.

### Things To Know
There are a lot of parameters which will be different depending on the concrete deployment and which are
not known at the moment of creating the Docker image.

To set these parameters Contraxsuite uses Docker Swarm configs support - ability to bind a config file from 
the host machine to be seen at the specific path inside the Docker container.
To fulfill the deployment parameters such config files are distributed as templates containing 
environment variables which are substituted with the values at the moment of cluster deployment.
It works similar to the following:
* deploy-contraxsuite-to-swarm-cluster.sh
    * load environment variables from setenv.sh (which also loads setenv_local.sh)
    * prepare docker compose configs:
        * take nginx config template
        * replace environment variables with values in the template
        * use the config in docker-compose file
        * ...
    * fill additional environment variables in docker-compose file which are made available inside the containers.

For storing persistent data Contraxsuite uses simple Docker volumes mounted to the filesystem of the 
host machine. A directory in the host file system is mounted to a directory inside the Docker container.
When Docker container is restarted all changes to its internal filesystem are lost excepting the changes
to the mounted volumes.
We don't use distributed filesystems to avoid bigger complexity of the deployments.
But when using simple FS volumes a user need to understand that when a container is started on a 
different host machine - it will have a different directory mounted. So for example if Postgres service
is changed so that it is started on another host machine the current database will be left on the
previous machine and a new clear one will be initialized on the new machine.
Volumes can be easily accessed from the host machine file system inside the docker work dir: 
/data/docker/volumes (/var/lib/docker/volumes).
They can be manually copied from one machine to another, backed up, restored.

## System Requirements
* Clean Ubuntu 16.04, 18.04 machine.
* At least 100GB free space on HDD at /.
* At least 16GB RAM.
* At least 8 CPU cores.

## Installation
* Obtain a VM with Ubuntu 16.04 or 18.04.
    * Open ports 80 (HTTP) and 443 (HTTPS).
    * Ensure you have access to the shell of the VM. 
* Setup Fully Qualified Domain Name (FQDN) for the VM.
* Install common utilities
* Download contents of this folder to the VM:
```
wget https://demo.contraxsuite.com/files/contraxsuite-deploy.tar.gz
tar -xzf contraxsuite-deploy.tar.gz
cd docker
```
* Obtain third-party paid dependencies:
    * jQWidgets (https://www.jqwidgets.com/download/)
    * Canvas HTML5 Template (https://themeforest.net/item/canvas-the-multipurpose-html5-template/9228123)
* Put zipped theme and jqwidgets files into ./deploy/dependencies directory and rename them to 
**jqwidgets.zip** and **theme.zip**.
  
  Contents of ./deploy/dependencies should be similar to this:
  * jqwidgets.zip - zipped JQWidgets Library
      * jqwidgets
        * globalization
        * styles
        * jqx-all.js
        * ...
  * theme.zip - zipped theme
      * Package-HTML
        * HTML
          * css
          * images
          * js
          * style.css
          
* Prepare the disk
    For an initial single-server installation it is enough to have a single disk with 
    at least 100GB at /. But for more safety it is usually a good idea to place Docker 
    on a separate 100GB disk. If for some reason all space is filled
    by Docker files you will avoid problems with logging in to the VM because the root
    partition will still have free space.
    
    If you decide to create a separate disk then mount it at **/data** before running the
    setup script (next step).
    For AWS use these instructions to make a separate disk available: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html 
      
* Run script: **setup_local_contraxsuite_ubuntu_16_04.sh** and enter the information which it requests.
  
  The script will do the following:
  * install Docker, 
  * initialize Docker Swarm cluster consisting of this single machine, 
  * download the latest Contraxsuite Docker image from Docker Hub, 
  * deploy services configured in ./deploy/docker-compose-single-host.yml file.
  
  The script will request path to Docker work dir and will suggest **/data/docker** by default.
  It will move the Docker work dir to the path you specified and reconfigure Docker.
  The default value is ok for both cases - if either you mounted a separate disk at /data
  or decided to use a single disk.
    
* Wait few minutes for all components to start.
Make sure all components have been started:
```
sudo docker service ls
```
The output should look like this (every service has at least one container started):
```

```

Docker Swarm cluster configuration (services, restrictions, e.t.c.) is in the docker-compose file specified
in setenv.sh (setenv_local.sh) in "DOCKER_COMPOSE_FILE" variable.

* After the installation is finished:
  * Django-based UI of the Contraxsuite application: **https://your.domain.com/advanced/**;
  * Jupyter with access to the Contraxsuite python code and database: **https://your.domain.com/jupyter/**;
  * Kibana connected to ElasticSearch to which Contraxsuite indexes documents and write logs: **https://your.domain.com/kibana/**
    * Contraxsuite Django logs are in **logstash*** indexes
    * Documents indexed for search purposes are in **contraxsuite*** indexes. 

  **Admin login/pass: Administrator/Administrator**
  
## Updating to the Latest Contraxsuite Image
To update running Contraxsuite demo application installed by these scripts to
to the latest version you can run the following script on the machine: 
**update_local_contraxsuite_to_latest_version.sh**

Database and documents uploaded to the system will be preserved after update.

## Advanced Usage

For more complicated deployments and support please contact LexPredict team. 