#!/bin/bash

echo "Installing custom SSL certificates if required"
ls -l /ssl_certs

for filename in /ssl_certs/*; do
    if [ ! -f "${filename}" ]; then
        continue
    fi

    venv_lib_dir="/contraxsuite_services/venv/lib"
    for python_dir in $(ls "${venv_lib_dir}"|grep python); do
        python_venv_dir="${venv_lib_dir}/${python_dir}"
        echo "" >> ${python_venv_dir}/site-packages/certifi/cacert.pem
        cat ${filename} >> ${python_venv_dir}/site-packages/certifi/cacert.pem
        filename=$(basename "$filename")
        echo "Added certificate ${filename} into ${python_venv_dir}/site-packages/certifi/cacert.pem"
    done
done
