FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive

COPY ./temp/contraxsuite_services /contraxsuite_services
COPY ./temp/python-requirements-additional.txt /contraxsuite_services/python-requirements-additional.txt
COPY ./temp/additionals /
COPY ./temp/build.info /
COPY ./temp/build.uuid /
COPY ./start.sh /
COPY ./hash_sums.sh /
COPY ./dump.sh /contraxsuite_services
COPY ./check_celery.sh /
COPY ./config-templates /config-templates
COPY ./temp/static /static
ENV LANG C.UTF-8

RUN echo "deb mirror://mirrors.ubuntu.com/mirrors.txt bionic main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb mirror://mirrors.ubuntu.com/mirrors.txt bionic-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb mirror://mirrors.ubuntu.com/mirrors.txt bionic-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    apt-get -y update --fix-missing && \
    apt-get install -y -q apt-utils lsb-release gcc-5 software-properties-common wget apt-transport-https locales && \
	echo "Ubuntu version: " && lsb_release -a && \
	echo "GCC 5 version: " && gcc-5 -v && \
	wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
	add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" && \
	wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add - && \
	echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-6.x.list && \
	add-apt-repository -y ppa:openjdk-r/ppa && \
	apt-get -y update --fix-missing && \
	apt-get install -y openjdk-8-jdk postgresql-client-9.6 && \
	cat /contraxsuite_services/deploy/base/debian-requirements.txt \
    | grep -v -E "^postgresql$" \
    | grep -v -E "^#" \
    | xargs -r apt-get -y -q install && \
	locale-gen --purge  en_US en_US.UTF-8 && \
	echo -e \'LANG="en_US.UTF-8"\nLANGUAGE="en_US:en"\n\' > /etc/default/locale && \
	npm -g install yuglify && \
	virtualenv -p /usr/bin/python3 /contraxsuite_services/venv && chmod ug+x /contraxsuite_services/venv/bin/activate && \
	. /contraxsuite_services/venv/bin/activate && python --version && pip install -r /contraxsuite_services/deploy/base/python-requirements-all.txt && pip uninstall -y -r /contraxsuite_services/deploy/base/python-unwanted-requirements.txt && pip install -r /contraxsuite_services/python-requirements-additional.txt && deactivate && \
	if [ -f  /contraxsuite_services/deploy/base/customer-requirements.txt ]; then \
    . /contraxsuite_services/venv/bin/activate && \
    pip install -r /contraxsuite_services/deploy/base/customer-requirements.txt && deactivate; fi && \
    . /contraxsuite_services/venv/bin/activate && python -m nltk.downloader averaged_perceptron_tagger punkt stopwords words maxent_ne_chunker wordnet && deactivate && \
    apt-get install -y curl && \
    cat /build.info && cat /build.uuid && ls /static -l && \
    apt-get purge -y gcc-5 build-essential linux-headers* && \
	apt-get clean autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    rm -rf /root/.cache/pip/ && \
    rm -rf /lexpredict-contraxsuite-core/.git/ && \
    rm -rf /var/lib/apt/lists && \
	wget https://github.com/krallin/tini/releases/download/v0.6.0/tini -O /usr/bin/tini && \
	chmod +x /usr/bin/tini
 
ENTRYPOINT ["/usr/bin/tini", "--"]
