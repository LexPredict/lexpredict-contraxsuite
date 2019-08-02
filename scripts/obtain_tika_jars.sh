TARGET_FOLDER=../contraxsuite_services/tika_jars
TIKA_VERSION=1.22
TIKA_SERVER_URL=https://www.apache.org/dist/tika/tika-app-$TIKA_VERSION.jar
IMAGIO_SERVER_URL=https://repo1.maven.org/maven2/com/github/jai-imageio

cd $TARGET_FOLDER
curl -sSL https://people.apache.org/keys/group/tika.asc -o /tmp/tika.asc && \
gpg --import /tmp/tika.asc && \
curl -sSL "$TIKA_SERVER_URL.asc" -o /tmp/tika-app-${TIKA_VERSION}.jar.asc && \
NEAREST_TIKA_SERVER_URL=$(curl -sSL http://www.apache.org/dyn/closer.cgi/${TIKA_SERVER_URL#https://www.apache.org/dist/}\?asjson\=1 \
    | awk '/"path_info": / { pi=$2; }; /"preferred":/ { pref=$2; }; END { print pref " " pi; };' \
    | sed -r -e 's/^"//; s/",$//; s/" "//') && \
echo "Nearest mirror: $NEAREST_TIKA_SERVER_URL" && \
curl -sSL "$NEAREST_TIKA_SERVER_URL" -o ./tika-app.jar

curl -sSL "$IMAGIO_SERVER_URL/jai-imageio-core/1.4.0/jai-imageio-core-1.4.0.jar" -o ./jai-imageio-core.jar
curl -sSL "$IMAGIO_SERVER_URL/jai-imageio-jpeg2000/1.3.0/jai-imageio-jpeg2000-1.3.0.jar" -o ./jai-imageio-jpeg.jar

apt install -y maven
rm -rf ./tika-src/
mkdir ./tika-src/
cd ./tika-src/
cp -fu ../../../docker/build/contraxsuite-app/tika/tika.config ../tika.config
git clone https://github.com/LexPredict/tika-server.git;
cd ./tika-server/lexpredict-tika/
mvn install -e -DskipTests;
cp -fu ./target/lexpredict-tika-1.0.jar ../../../lexpredict-tika.jar
cd ../../../
rm -rf tika-src/
