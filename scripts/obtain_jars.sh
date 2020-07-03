#!/bin/bash

# WARNING: JAR file names are referenced in settings.py/local_settings.py
set -e

TARGET_FOLDER=../contraxsuite_services/jars
TIKA_VERSION=1.24.1
TIKA_SERVER_URL=https://www.apache.org/dist/tika/tika-app-$TIKA_VERSION.jar
IMAGIO_SERVER_URL=https://repo1.maven.org/maven2/com/github/jai-imageio

cd $TARGET_FOLDER

pwd

if [ -z "${TIKA_JAR_URL}" ]; then
    echo "Downloading: $TIKA_SERVER_URL.asc" && \
    curl -sSL --fail "$TIKA_SERVER_URL.asc" > /tmp/tika-app-${TIKA_VERSION}.jar.asc && \
    NEAREST_TIKA_SERVER_URL=$(curl -sSL --fail http://www.apache.org/dyn/closer.cgi/${TIKA_SERVER_URL#https://www.apache.org/dist/}\?asjson\=1 \
        | awk '/"path_info": / { pi=$2; }; /"preferred":/ { pref=$2; }; END { print pref " " pi; };' \
        | sed -r -e 's/^"//; s/",$//; s/" "//') && \
    echo "Nearest mirror: $NEAREST_TIKA_SERVER_URL" && \
    curl -sSL --fail "$NEAREST_TIKA_SERVER_URL" > ./tika-app.jar || exit 1
else
    echo "TIKA jar url: ${TIKA_JAR_URL}" && \
    curl -sSL --fail "${TIKA_JAR_URL}" > ./tika-app.jar || exit 1
fi
echo "Downloading jai libs..."

curl -sSL --fail "$IMAGIO_SERVER_URL/jai-imageio-core/1.4.0/jai-imageio-core-1.4.0.jar" > ./jai-imageio-core.jar || exit 1
curl -sSL --fail "$IMAGIO_SERVER_URL/jai-imageio-jpeg2000/1.3.0/jai-imageio-jpeg2000-1.3.0.jar" > ./jai-imageio-jpeg2000.jar || exit 1

sudo apt install -y maven
if [ -d ./tika-src/ ]; then
  rm -rf ./tika-src/
fi
mkdir ./tika-src/
cd ./tika-src/
cp -fu ../../../docker/build/contraxsuite-app/tika/tika.config ../tika.config
cp -fu ../../../docker/build/contraxsuite-app/tika/tika.lexp.config ../tika.lexp.config
git clone https://github.com/LexPredict/tika-server.git;
cd ./tika-server/lexpredict-tika/
mvn install -e -DskipTests;
cp -fu ./target/lexpredict-tika-1.0.jar ../../../lexpredict-tika.jar
cd ../../../
if [ -d tika-src/ ]; then
  rm -rf tika-src/
fi
if [ -d ./tika-src/ ]; then
  rm -rf ./tika-src/
fi
