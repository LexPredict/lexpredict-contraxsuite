Prerequisites
=========================

.. note:: This documentation is under active development. 
   As such, pages like this one are currently incomplete.

Installing ContraxSuite requires the following technologies:

* git
* Python 3.6
* Python virtual environments
* Docker
* Kubernetes

Please set up and configure these technologies on your respective system. Special considerations are detailed below. 

System Requirements
--------------------------

System resource requirements vary depending on usage scale. A basic installation with no more than 3 concurrent users fewer than 500 documents and can run with constrained resources.
Reliable production environments should be deployed on systems with at least the suggested requirements.

ContraxSuite will run on both virtual and physical systems and requires the following:

* Fully-qualified domain name (FQDN) attached to the server
* Network access: Port 22 (SSH), 80 (HTTP), 443 (HTTPS)
* Ports 80 and 443 open on the firewall level

Minimum Requirements
^^^^^^^^^^^^^^^^^^^^
+------------+---------+
| CPU        | 4 cores |
+------------+---------+
| RAM        | 8 GB    |
+------------+---------+
| Free Space | 5 GB    |
+------------+---------+

Suggested Requirements
^^^^^^^^^^^^^^^^^^^^^^
+------------+---------+
| CPU        | 8 cores |
+------------+---------+
| RAM        | 16 GB   |
+------------+---------+
| Free Space | 100 GB  |
+------------+---------+

Python Virtual Environment
--------------------------

.. TODO: figure out if we can somehow link the requirements.txt file to rst files; this would auto-updated the required version of Python.

Use your preferred Python virtual environment manager (`Python venv`_ or `Anaconda`_) to set up a virtual environment with Python 3.6.x.

.. warning::
    ContraxSuite is untested on Python >=3.7.
    Some users report Scikit-Learn conflicts using Python >=3.7. 

.. warning::
    Hyperlinks
        Python venv: https://docs.python.org/3.6/library/venv.html
        Anaconda: https://www.anaconda.com/

.. _Python venv: https://docs.python.org/3.6/library/venv.html
.. _Anaconda: https://www.anaconda.com/