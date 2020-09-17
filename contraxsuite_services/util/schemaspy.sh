#!/bin/bash

# Generates schema of the database using schemaspy.
# Output is: set of html, png and other files in schemaspy_output dir.
# Requires Oracle Java 8
# Requires Graphviz (sudo apt-get install graphviz)

source setenv.sh

mkdir -p schemaspy_output

java -jar schemaspy/schemaspy-6.0.0-rc2.jar \
-t pgsql -dp schemaspy/postgresql-42.1.4.jar \
-loadjars \
-host ${contrax_db_host} \
-port ${contrax_db_port} \
-u ${contrax_db_user} \
-p ${contrax_db_password} \
-db ${contrax_db_name} \
-o ./schemaspy_output
