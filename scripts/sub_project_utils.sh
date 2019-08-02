#!/bin/bash

add_line_if_not_exists () {
	DST_FILE=$1
	LINE=$2
	echo Adding "${LINE}" to "${DST_FILE}"
	grep -q -F "${LINE}" ${DST_FILE} || echo "${LINE}" | tee --append ${DST_FILE}
}

mount_sub_project_folder () {
        REL_FOLDER=$1
	echo Mounting "${CURDIR}/${REL_FOLDER}" to "${CONTRAXSUITE_SERVICES_PROJECT_ROOT}/${REL_FOLDER}"
	ln -s "${CURDIR}/${REL_FOLDER}" "${CONTRAXSUITE_SERVICES_PROJECT_ROOT}/${REL_FOLDER}"

	add_line_if_not_exists "${CONTRAXSUITE_SERVICES_PROJECT_ROOT}/.gitignore" "${REL_FOLDER}"
}

unmount_sub_project_folder () {
	REL_FOLDER=$1
        echo Removing "${CURDIR}/${REL_FOLDER}" from "${CONTRAXSUITE_SERVICES_PROJECT_ROOT}/${REL_FOLDER}"
        rm -rf "${CONTRAXSUITE_SERVICES_PROJECT_ROOT}/${REL_FOLDER}"
}
