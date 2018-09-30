#!/usr/bin/env bash

set -e

GIT_DICT_DATA_REPO_ROOT='https://raw.githubusercontent.com/LexPredict/lexpredict-legal-dictionary/1.0.6'
TERM_URLS=('accounting/ifrs_iasb.csv' 'accounting/uk_gaap.csv' 'accounting/us_fasb.csv'
                  'accounting/us_gaap.csv' 'accounting/us_gasb.csv' 'financial/financial.csv'
                  'legal/common_law.csv' 'legal/us_cfr.csv' 'legal/us_usc.csv' 'legal/common_US_terms_top1000.csv'
                  'scientific/us_hazardous_waste.csv')
COURTS_URLS=('legal/ca_courts.csv' 'legal/us_courts.csv')
GEOENTITIES_URLS=('geopolitical/geopolitical_divisions.csv')

function load_dict() {
    ROOT_URL=$1
    DICT_URLS=( "$2" )
    FOLDER=$3
    mkdir -p ${FOLDER}
    pushd ${FOLDER}

    for DICT_URL in ${DICT_URLS[@]}; do
        wget ${ROOT_URL}/${DICT_URL}
    done

    popd
}

mkdir -p ./.tmp_dict
pushd ./.tmp_dict

load_dict "${GIT_DICT_DATA_REPO_ROOT}/en" "$(echo ${TERM_URLS[@]})" 'terms'
load_dict "${GIT_DICT_DATA_REPO_ROOT}/en" "$(echo ${COURTS_URLS[@]})" 'courts'
load_dict "${GIT_DICT_DATA_REPO_ROOT}/multi" "$(echo ${GEOENTITIES_URLS[@]})" 'geoentities'
zip -r dict_data_en.zip *

popd

mv ./.tmp_dict/dict_data_en.zip ./
rm -r ./.tmp_dict
