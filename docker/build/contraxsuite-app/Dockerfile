FROM ubuntu:16.04

# Update apt first time - initial ubuntu image contains no data
RUN apt-get -y update --fix-missing
RUN apt-get install -y -q apt-utils

RUN apt-get install -y -q lsb-release

RUN echo "Ubuntu version: " && lsb_release -a

RUN apt-get install -y -q gcc-5

RUN echo "GCC 5 version: " && gcc-5 -v

# This is required to get add-apt-repository command working
RUN apt-get install -y -q build-essential software-properties-common python-software-properties



## Add apd repositories for all required components
RUN apt-get install -y wget

RUN apt-get install -y apt-transport-https

# Install apt repositories
RUN \
 add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" \
 && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
 && wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add - \
 && echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-6.x.list \
 && add-apt-repository -y ppa:openjdk-r/ppa \
 && apt-get -y update --fix-missing

RUN apt-get install -y openjdk-8-jdk

RUN apt-get install -y postgresql-9.6


COPY ./temp/contraxsuite_services /contraxsuite_services


# Install everything from debian requirements file excepting postgres server - it will be on another docker image
RUN cat /contraxsuite_services/deploy/base/debian-requirements.txt \
    | grep -v -E "^postgresql$" \
    | grep -v -E "^#" \
    | xargs -r apt-get -y -q install

# Install locales
RUN locale-gen --purge  en_US en_US.UTF-8
RUN echo -e \'LANG="en_US.UTF-8"\nLANGUAGE="en_US:en"\n\' > /etc/default/locale

ENV LANG C.UTF-8

RUN npm -g install yuglify
RUN ln -s /usr/bin/nodejs /usr/bin/node


RUN virtualenv -p /usr/bin/python3 /contraxsuite_services/venv && chmod ug+x /contraxsuite_services/venv/bin/activate
RUN . /contraxsuite_services/venv/bin/activate && python --version

# Install python requirements
RUN . /contraxsuite_services/venv/bin/activate && \
    pip install -r /contraxsuite_services/deploy/base/python-requirements-all.txt


COPY ./temp/python-requirements-additional.txt /contraxsuite_services/python-requirements-additional.txt
COPY ./temp/additionals /

RUN . /contraxsuite_services/venv/bin/activate && \
    pip install -r /contraxsuite_services/python-requirements-additional.txt

RUN . /contraxsuite_services/venv/bin/activate && \
    python -m nltk.downloader averaged_perceptron_tagger punkt stopwords words maxent_ne_chunker wordnet

RUN apt-get install -y curl

COPY ./temp/build.info /
COPY ./temp/build.uuid /
COPY ./start.sh /
COPY ./check_celery.sh /
COPY ./config-templates /config-templates
COPY ./temp/static /static

WORKDIR /contraxsuite_services

RUN cat /build.info
RUN cat /build.uuid
RUN ls /static -l

RUN apt-get clean autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

# kernel crashes.
ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]
