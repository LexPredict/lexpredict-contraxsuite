#!/bin/bash

CONTRAX_FILE_STORAGE_WEBDAV_ROOT_URL=http://${DOCKER_WEBDAV_SERVER_NAME}:80

ensure_webdav_dir () {
  local SRC_FILES_DIR=$1
  IFS='/' read -r -a array <<<"${SRC_FILES_DIR}"
  local TEMP
  for el in "${array[@]}"
  do
    TEMP=$TEMP/$el
    local folder_path=${CONTRAX_FILE_STORAGE_WEBDAV_ROOT_URL%%*(/)}/${TEMP:1}
    local folder_proper_path=${folder_path%%*(/)}/
    echo "Ensure folder: ${folder_proper_path}"
    curl -u ${DOCKER_WEBDAV_AUTH_USER}:${DOCKER_WEBDAV_AUTH_PASSWORD} \
    -X MKCOL "${folder_proper_path}"
  done
}

upload_files_to_webpath () {
    local SRC_FILES_DIR=$1
    local DST_FILES_DIR=$2
    local FILE_PREFIX=$3

    echo "Wating for WebDav ..."
    while ! curl -u ${DOCKER_WEBDAV_AUTH_USER}:${DOCKER_WEBDAV_AUTH_PASSWORD} ${CONTRAX_FILE_STORAGE_WEBDAV_ROOT_URL} 2>&1 | grep 'html'
    do
      echo "Sleeping 5 more seconds to let WebDAV start"
      sleep 5
    done

    pushd "${SRC_FILES_DIR}" > /dev/null
    local FN
    for FN in $(find -L ./ -type f); do
        popd > /dev/null
        local dest_subfolder=$(dirname ${FN})
        ensure_webdav_dir ${DST_FILES_DIR}${dest_subfolder:1}
        local dst_file_name=${FILE_PREFIX}$(basename ${FN:2})
        local dst_full_path=${DST_FILES_DIR}${dest_subfolder:1}/${dst_file_name}
        local dst_url=${CONTRAX_FILE_STORAGE_WEBDAV_ROOT_URL%%*(/)}/${dst_full_path}
        echo "Upload template file to ${dst_url}"
        curl -u ${DOCKER_WEBDAV_AUTH_USER}:${DOCKER_WEBDAV_AUTH_PASSWORD} -T "${SRC_FILES_DIR}/${FN}" "${dst_url}"
        pushd "${SRC_FILES_DIR}" > /dev/null
    done
    popd > /dev/null
}
