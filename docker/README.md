# LexPredict ContraxSuite - Software
Software package for [LexPredict ContraxSuite](https://github.com/LexPredict/lexpredict-contraxsuite).

* Official Website: https://contraxsuite.com/
* LexPredict: https://lexpredict.com/
* [Current Documentation](https://github.com/LexPredict/lexpredict-contraxsuite/blob/master/documentation/)
* Contact: contact@lexpredict.com
* Support Questions: support@contraxsuite.com
* Professional Services, Support Contracts, Commercial Services: contact@lexpredict.com

![Logo](https://www.lexpredict.com/wp-content/uploads/2014/08/lexpredict_logo_horizontal_1.png)

## Licensing
ContraxSuite is available under a dual-licensing model as described here:
 * https://www.lexpredict.com/2017/07/30/licensing-contraxsuite-legaltech-dual/

**If you would like to request a release from the terms of the default AGPLv3 license, please contact us at: ContraxSuite Licensing <<license@contraxsuite.com>>.**

## Structure
Please note that ContraxSuite installations generally require trained models or knowledge sets for usage.
* ContraxSuite web application: https://github.com/LexPredict/lexpredict-contraxsuite
* LexNLP library for extraction: https://github.com/LexPredict/lexpredict-lexnlp
* ContraxSuite pre-trained models and "knowledge sets": https://github.com/LexPredict/lexpredict-legal-dictionary
* ContraxSuite agreement samples: https://github.com/LexPredict/lexpredict-contraxsuite-samples
* ContraxSuite deployment automation: https://github.com/LexPredict/lexpredict-contraxsuite-deploy

# Contraxsuite: Deployment

This folder contains scripts for deploying the current latest Contraxsuite release on a clean Ubuntu 16.04 or 18.04 machine.

## Architecture

Contraxsuite is a Python/Django based application.

Contraxsuite deployment consists of the following main components:
* Django Web application (UWSGI) - Django-based UI, REST API
* PostgreSQL - Relational database
* Celery Beat Scheduler - Periodical tasks scheduling
* Celery Workers (1 or more) - Asynchronous task processing
* RabbitMQ - Message queue for Celery
* Flower - Celery management UI
* Jupyter - Jupyter Notebook application connected to the Contraxsuite code and DB for experimenting
* Elasticsearch - Full text search, log storage
* Tika REST Servers (1 or more) - Text extraction from different file formats
* Filebeat - Logs collecting
* Metricbeat - Metrics collecting
* Kibana - Web UI for accessing Elasticsearch data, logs, metrics
* Nginx - Web server and reverse proxy server routing request among the web backends, HTTPS support
* Docker - Performs operating-system-level virtualization, also known as "containerization". 

To simplify the deployment and management of these components the Contraxsuite platform uses Docker containers and the Docker Swarm clustering platform.

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
There are a lot of parameters which will be different depending on your deployment requirements and goals, so we cannot have a one-size fits all deployment package.

To set these parameters Contraxsuite uses Docker Swarm configs feature - ability to bind a config file from 
the host machine to be seen at the specific path inside the Docker container.

To allow having different parameters depending on the deployment the config files are distributed as templates containing 
environment variables which are substituted with the values at the moment of cluster deployment.

It works similar to the following:
* deploy-contraxsuite-to-swarm-cluster.sh runs and does the following:
    * loads environment variables from setenv.sh (which also loads setenv_local.sh)
    * prepares docker compose configs:
        * takes nginx config template
        * replaces environment variables with values in the template
        * uses the config in docker-compose file
        * ...
    * fills additional environment variables in docker-compose file which are made available inside the containers.

For storing persistent data Contraxsuite uses simple Docker volumes mounted to the filesystem of the 
host machine. A directory in the host file system is mounted to a directory inside the Docker container.
When the Docker container is restarted all changes to its internal filesystem are lost excepting the changes
to the mounted volumes.

We don't use distributed filesystems to avoid bigger complexity of the deployments.
But when using simple FS volumes a user need to understand that when a container is started on a 
different host machine - it will have a different directory mounted. So for example if the PostgreSQL service
is changed so that it is started on another host machine the current database will be left on the
previous machine and a new clear one will be initialized on the new machine.

Volumes can be easily accessed from the host machine file system inside the docker work dir: 
/data/docker/volumes (/var/lib/docker/volumes).
They can be manually copied from one machine to another, backed up, restored.

## System Requirements
* Clean Ubuntu 16.04, 18.04 machine.
* Either Virtual or Physical PCs are supported
* Network Access: Port 22 (SSH), 80 (HTTP), 443 (HTTPS)
* RAM: 16GB.
* CPU: 8 cores.
* Storage: 
    * Either 100GB disk at / 
    * or 32GB disk at / for the OS and an additional 100GB disk at /data for Docker and Contraxsuite (safer). Note: Creating, mounting and formatting the disk is outside of the scope of this readme, but detailed instructions can easily be found online.

## Installation
**We make simplifying assumptions throughout this installation to work for most initial use cases. Deviations from this setup guide will require you to be proficient in a wide range of applications, including those described above. **
* Obtain a VM with Ubuntu 16.04 or 18.04.
    * Open ports 80 (HTTP) and 443 (HTTPS).
    * Ensure you have access to the shell of the VM. 
* Setup a Fully Qualified Domain Name (FQDN) for the VM if you are going to access it in the Internet
and going to setup HTTPS certificates.
* Download contents of this folder to the VM:
    ```
    sudo apt-get install -y wget
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
    at least 100GB at /. If you just want to learn the system you can ignore this step.
    
    To check free space on your disks use:
    ```
    df -h
    ```
    
    For more safety it is usually a good idea to place Docker 
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
    
    The following data will be requested by the setup script:
    1. Domain name of this machine. 
    If you have FQDN - enter it. If you are installing Contraxsuite on a local VMWare/Virtualbox VM - leave "localhost".
    2. Docker work dir. 
    Default **/data/docker** usually works good for both 
    cases - either if you mounted a separate disk to /data or if you decided to leave /data at the root 
    disk. By default Docker installs itself to /var/lib/docker and the setup script will move it to the
    directory you specified.
    3. Deployment type: single-server or one master + many workers.
    Use single-server deployment for first-time installations. Multi-worker installations require manual cluster 
    configuration which is outer of the scope of this readme.
    4. Do you need Letsencrypt certificates or not.
    If you are going to access Contraxsuite via the Internet it is better to use HTTPS instead of HTTP.
    If you agree to setup the certificates the script will install "certbot" from Letsencrypt, prepare
    the certificates and configure Contraxsuite to use them.
    Take into account that "certbot" will ask few more questions like: overall confirmation, email address,
    allow sharing the email address on the Letsencrypt side e.t.c.
    5. Internal IP address for Docker Swarm cluster.  
    This IP address will be used for advertising in Docker Swarm. 
    By default Docker Swarm tries to detect the address on its own but for example at Digital Ocean
    the VMs have two IP addresses at the main network interface - one internal and one public external address
    which is seen from the Internet.
    To avoid ambiguities the script requests user to check and enter the internal IP address.
    Before asking the address the script will print the available network interfaces and all their addresses
    similar to this:
    ```
    1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
        link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
        inet 127.0.0.1/8 scope host lo
           valid_lft forever preferred_lft forever
    2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
        link/ether ca:73:9c:80:40:71 brd ff:ff:ff:ff:ff:ff
        inet 104.248.176.29/20 brd 104.248.191.255 scope global eth0
           valid_lft forever preferred_lft forever
        inet 10.46.0.6/16 brd 10.46.255.255 scope global eth0
           valid_lft forever preferred_lft forever
    3: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
        link/ether 02:42:9f:31:2c:d1 brd ff:ff:ff:ff:ff:ff
        inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
           valid_lft forever preferred_lft forever
    10: docker_gwbridge: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
        link/ether 02:42:e8:e7:a6:35 brd ff:ff:ff:ff:ff:ff
        inet 172.19.0.1/16 brd 172.19.255.255 scope global docker_gwbridge
           valid_lft forever preferred_lft forever
    
    ```
    In this example:
    "lo" - is the local interface, ignore it.
    "eth0" - is the main network interface having two IP addresses: 104.248.176.29 (external) and 10.46.0.6 (internal).
    You need to enter the internal IP address: 10.46.0.6 .

* Wait few minutes for all components to start.
Make sure all components have been started:
```
sudo docker service ls
```
The output should look like this (every service has at least one container started):
```
root@ubuntu-s-4vcpu-8gb-sfo2-01:~/docker# sudo docker service ls
ID                  NAME                                      MODE                REPLICAS            IMAGE                                                     PORTS
g8dms9vvrwds        contraxsuite_contrax-celery               global              1/1                 lexpredict/lexpredict-contraxsuite:latest                 
lq3fzpzx4x9v        contraxsuite_contrax-celery-beat          replicated          1/1                 lexpredict/lexpredict-contraxsuite:latest                 
vcmflc3s7wuc        contraxsuite_contrax-curator_filebeat     replicated          1/1                 stefanprodan/es-curator-cron:latest                       
3qn6lw1uq1xx        contraxsuite_contrax-curator_metricbeat   replicated          0/0                 stefanprodan/es-curator-cron:latest                       
pijk7xt7icwx        contraxsuite_contrax-db                   replicated          1/1                 postgres:9.6                                              
mn757ymafzog        contraxsuite_contrax-elasticsearch        replicated          1/1                 docker.elastic.co/elasticsearch/elasticsearch-oss:6.2.4   
4d6gmjg0f50g        contraxsuite_contrax-filebeat             global              1/1                 docker.elastic.co/beats/filebeat:6.2.4                    
vxhpg8fw5szq        contraxsuite_contrax-flower               replicated          0/0                 lexpredict/lexpredict-contraxsuite:latest                 
n9er4kdg939b        contraxsuite_contrax-jupyter              replicated          1/1                 lexpredict/lexpredict-contraxsuite:latest                 
poug8ydxkz26        contraxsuite_contrax-kibana               replicated          1/1                 docker.elastic.co/kibana/kibana-oss:6.2.4                 
xseorkylt3p0        contraxsuite_contrax-logrotate            global              1/1                 tutum/logrotate:latest                                    
1b451ku22b14        contraxsuite_contrax-metricbeat           replicated          0/0                 docker.elastic.co/beats/metricbeat:6.2.4                  
quopp5ak19k3        contraxsuite_contrax-nginx                replicated          1/1                 nginx:stable                                              *:80->8080/tcp, *:443->4443/tcp
ixkkplnixtmr        contraxsuite_contrax-rabbitmq             replicated          1/1                 rabbitmq:3-management                                     
xc6axmngyygo        contraxsuite_contrax-tika                 global              1/1                 lexpredict/tika-server:latest                             
tl1iu3b8gj7f        contraxsuite_contrax-uwsgi                replicated          1/1                 lexpredict/lexpredict-contraxsuite:latest  

```

You can see the logs of any service using a command similar to:
```
sudo docker service logs -f contraxsuite_contrax-uwsgi
```

Docker system logs can be seen this way:
```
sudo tail -f /var/log/syslog
```

* After the installation is finished:
  * Django-based UI of the Contraxsuite application: **https://your.domain.com/advanced/**;
  * Jupyter with access to the Contraxsuite python code and database: **https://your.domain.com/jupyter/**;
  * Kibana connected to ElasticSearch to which Contraxsuite indexes documents and write logs: **https://your.domain.com/kibana/**
    * Contraxsuite Django logs are in **logstash*** indexes
    * Documents indexed for search purposes are in **contraxsuite*** indexes.
  * Root (https://your.domain.com/) is reserved for the new React UI provided to the paid 
  customers. See https://demo.contraxsuite.com .

  **Admin login/pass: Administrator/Administrator**
  
* To prepare text processing system and to additionally ensure that Celery works:
    * Login to https://your.domain.com/advanced/ as Administrator
    **Web app will continue responding with 502 error until the UWSGI service is fully loaded.
    Wait few minutes till it start showing the login screen.**
    * Go to Tasks / Admin Tasks in the top menu (https://your.domain.com/advanced/task/task/list/)
    * Click Run Task, select Load Data / Load Dictionary Data. Set all checkboxes and run the task.
    * Wait a minute and click Refresh Data icon (rotating arrows) to refresh the task progress.
    The tasks should end soon.
  
## Updating to the Latest Contraxsuite Image
To update running Contraxsuite demo application installed by these scripts to
to the latest version you can run the following script on the machine: 
**update_local_contraxsuite_to_latest_version.sh**

Database and documents uploaded to the system will be preserved after update.

## Troubleshooting

1. If something went wrong you can fully remove Contraxsuite and all data with the following commands. Note: this assumes you installed to the `/data` directory, so please adjust this line if you installed it elsewhere.
```
sudo service docker stop
sudo apt-get remove docker-ce
sudo rm -rf /data
```
After this you can re-install Contraxsuite with the setup script (see above).

2. If at some point Docker gives errors that updating configs is not allowed or updating service modes is not 
allowed e.t.c. the solution is to remove the Contraxsuite stack and re-deploy. 
Current version of Docker does not support changing configs and some other important service parameters. 
```
sudo docker stack rm contraxsuite
sleep 60
./deploy-contraxsuite-to-swarm-cluster.sh
```

3. If you see that some service does not start its containers for too long...
For example the output of
```
sudo docker service ls
```
looks like this:
```
...
0vazerwzavx7        contraxsuite_contrax-nginx                replicated          0/1                 nginx:stable                                              *:80->8080/tcp, *:443->4443/tcp
...
```
See: "0/1" - it is going to start 1 task/container but only 0 is started at the moment.
First check the service logs:
```
sudo docker service logs -f contraxsuite_contrax-nginx
```
If there are visible problems in the service logs - fix them and either wait or restart Docker (sudo service docker restart).

If the logs are totally empty then this usually means that Docker was unable to find the required image or have some other
system-wide problems.

Check Docker errors in syslog:
```
sudo tail -f /var/log/syslog
```

For more complicated deployments and support please contact the LexPredict team at support@contraxsuite.com
