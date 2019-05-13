#!/bin/bash

get_fn_hash () {
    local FN=$1
    local FN_SUM=`echo ${FN} | md5sum | awk '{print $1}'`
    echo "FN_${FN_SUM}"
}

write_hash_sums () {
    local FILES_DIR=$1
    local DST_SUMS_FILE=$2
    # Calculate md5 sum of each file in the SRC_FILES_DIR recursively and write each sum into
    # a file having the same relative path as the source file but placed into the dst dir.
    rm -f "${DST_SUMS_FILE}"

    pushd "${FILES_DIR}" > /dev/null
    local FN
    for FN in $(find -L ./ -type f); do
        local FN_HASH=`echo ${FN} | md5sum | awk '{print $1}'`
        local CONTENT_HASH=`md5sum ${FN} | awk '{print $1}'`
        popd > /dev/null
        echo "${FN_HASH} ${CONTENT_HASH}" >> "${DST_SUMS_FILE}"
        pushd "${FILES_DIR}" > /dev/null
    done
    popd > /dev/null
}

read_hash_sums () {
    local DICT_VAR_NAME=$1
    local SUMS_FILE=$2

    declare -A -g ${DICT_VAR_NAME}

    if [ -f "${SUMS_FILE}" ]; then
        while read FN_SUM CONTENT_SUM
        do
            eval "$DICT_VAR_NAME[FN_$FN_SUM]=$CONTENT_SUM"
        done < ${SUMS_FILE}
    fi
}

copy_unchanged_files () {
    local SRC_FILES_DIR=$1
    local DST_FILES_DIR=$2
    local ORIGINAL_HASHES_FILE=$3

    declare -A EXISTING_HASHES
    read_hash_sums EXISTING_HASHES ${ORIGINAL_HASHES_FILE}

    pushd "${SRC_FILES_DIR}" > /dev/null
    local FN
    for FN in $(find -L ./ -type f); do
        popd > /dev/null
        local ACTUAL_CONTENT_HASH

        local dst_dir="$(dirname ${DST_FILES_DIR}/${FN})"
        if [ -f "${DST_FILES_DIR}/${FN}" ]; then
            ACTUAL_CONTENT_HASH=`md5sum ${DST_FILES_DIR}/${FN} | awk '{print $1}'`
            local UNCHANGED_CONTENT_HASH=${EXISTING_HASHES[$(get_fn_hash $FN)]}

            if [ "$ACTUAL_CONTENT_HASH" == "$UNCHANGED_CONTENT_HASH" ]; then
                echo "Updating file: $FN, original hash: $UNCHANGED_CONTENT_HASH, actual hash: $ACTUAL_CONTENT_HASH"
                if [ ! -d "${dst_dir}" ]; then
                    echo "Creating dir: ${dst_dir}"
                    mkdir -p "${dst_dir}"
                fi
                cp "${SRC_FILES_DIR}/${FN}" "${DST_FILES_DIR}/${FN}"
            else
                if [ "" == "$UNCHANGED_CONTENT_HASH" ]; then
                    if [ ! -d "${dst_dir}" ]; then
                        echo "Creating dir: ${dst_dir}"
                        mkdir -p "${dst_dir}"
                    fi
                    cp "${SRC_FILES_DIR}/${FN}" "${DST_FILES_DIR}/${FN}"
                else
                    echo "Ignoring file: $FN, original hash: $UNCHANGED_CONTENT_HASH, actual hash: $ACTUAL_CONTENT_HASH"
                fi
            fi
        else
            ACTUAL_CONTENT_HASH=
            echo "New file:      $FN, original hash: $UNCHANGED_CONTENT_HASH"
            if [ ! -d "${dst_dir}" ]; then
                echo "Creating dir: ${dst_dir}"
                mkdir -p "${dst_dir}"
            fi
            cp "${SRC_FILES_DIR}/${FN}" "${DST_FILES_DIR}/${FN}"
        fi
        pushd "${SRC_FILES_DIR}" > /dev/null
    done
    popd > /dev/null
    write_hash_sums ${SRC_FILES_DIR} ${ORIGINAL_HASHES_FILE}

}
