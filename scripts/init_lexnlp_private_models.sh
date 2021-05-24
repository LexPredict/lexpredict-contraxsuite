#!/bin/bash

DOCK_PATH=$(sudo docker volume inspect contraxsuite_contraxsuite_data_media | grep -o -P '(?<="Mountpoint": ")[^\"]+')
echo "Copying the following models to the docker volume:"
ls ../../lexpredict-lexnlp-models/output/classifiers/en

sudo cp -rn ../../lexpredict-lexnlp-models/output/classifiers/en ${DOCK_PATH}/data/models

echo "Current contents of the "models" folder in the docker volume:"
sudo ls ${DOCK_PATH}/data/models/en

