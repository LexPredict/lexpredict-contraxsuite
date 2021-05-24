#!/usr/bin/env bash

# ARGS:
# 1. PREVIOUS release number
# 2. NEW release number


# local paths
#PRIVATE_REPO_PATH="/home/alex/dev/michael/contraxsuite/lexpredict-contraxsuite-services"
#PUBLIC_REPO_PATH="/home/alex/dev/michael/contraxsuite/lexpredict-contraxsuite"

CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PRIVATE_REPO_PATH="$(readlink -f "$CURR_DIR/../../")"
PUBLIC_REPO_PATH="$(readlink -f "$CURR_DIR/../../../lexpredict-contraxsuite")"

DEV_BRANCH="develop"
PREV_RELEASE_NUM=$1
NEW_RELEASE_NUM=$2
LINE="================================================================="


# prompt if no args provided
if [ $# -ne 2 ]; then
    read -p "Enter PREVIOUS release number: " PREV_RELEASE_NUM
    if [ -z ${PREV_RELEASE_NUM} ]; then
        echo "Exiting program."
        return 1
    fi
    read -p "Enter NEW release number: " NEW_RELEASE_NUM
    if [ -z ${NEW_RELEASE_NUM} ]; then
        echo "Exiting program."
        return 1
    fi
fi


# check if NEW_RELEASE_NUM release branch exists
echo ${LINE}
echo "Update private@${NEW_RELEASE_NUM}"

pushd ${PRIVATE_REPO_PATH}

if [ -z "`git branch --list ${NEW_RELEASE_NUM}`" ]
then
   echo "'-private' branch ${NEW_RELEASE_NUM} doesn't exist. Exiting program."
   return 1
fi


# confirm further processing
echo ${LINE}
echo "Copy data from private@${NEW_RELEASE_NUM} to public@${NEW_RELEASE_NUM}, continue?" yn
select yn in "Yes" "No"; do
    case ${yn} in
        Yes ) break;;
        No ) return 1;;
    esac
done


git checkout ${NEW_RELEASE_NUM}
git pull origin ${NEW_RELEASE_NUM}

# replace old release number with new one in files' docstrings
echo ${LINE}
echo "Update version number in private@${NEW_RELEASE_NUM} from ${PREV_RELEASE_NUM} to ${NEW_RELEASE_NUM}"

#PREV_RELEASE_NUM_esc=$(echo ${PREV_RELEASE_NUM} | sed 's,\.,\\.,g')
#NEW_RELEASE_NUM_esc=$(echo ${NEW_RELEASE_NUM} | sed 's,\.,\\.,g')
#LATEST_COMMIT_HASH=$(git log --pretty=format:'%h' -n 1)
#find ./ -type f -readable -writable -exec sed -i "s/__version__ = \"$PREV_RELEASE_NUM_esc\"/__version__ = \"$NEW_RELEASE_NUM_esc\"/g" {} \;
#find ./ -type f -readable -writable -exec sed -i "s/blob\/$PREV_RELEASE_NUM_esc\/LICENSE/blob\/$NEW_RELEASE_NUM_esc\/LICENSE/g" {} \;
#sed -i "s/VERSION_NUMBER = '$PREV_RELEASE_NUM_esc'/VERSION_NUMBER = '$NEW_RELEASE_NUM_esc'/g" contraxsuite_services/settings.py
#sed -i "s/VERSION_COMMIT = '.\{7\}'/VERSION_COMMIT = '$LATEST_COMMIT_HASH'/g" contraxsuite_services/settings.py
#echo "${NEW_RELEASE_NUM}" > version.txt


# substitute name of release notes & changelog file
#RELEASE_NOTES_PATH="${PRIVATE_REPO_PATH}/documentation/Release Notes and Changelog - Release "
#[ -f "${RELEASE_NOTES_PATH}${PREV_RELEASE_NUM}.pdf" ] && \
#   mv "${RELEASE_NOTES_PATH}${PREV_RELEASE_NUM}.pdf" "${RELEASE_NOTES_PATH}${NEW_RELEASE_NUM}.pdf"


# push changes to a NEW_RELEASE_NUM branch
echo ${LINE}
echo "Push changes in private@${NEW_RELEASE_NUM} branch"
#git add --all
#git commit -m "CS: updated version from ${PREV_RELEASE_NUM} to ${NEW_RELEASE_NUM}"
#git push origin ${NEW_RELEASE_NUM}

# renew -private develop branch
echo "Push changes in private@${DEV_BRANCH} branch"
#git checkout ${DEV_BRANCH}
#git merge ${NEW_RELEASE_NUM}
#git push origin ${DEV_BRANCH}

# renew -private master branch
echo ${LINE}
echo "Push changes in private@master branch"
#git checkout master
#git merge ${NEW_RELEASE_NUM}
#git push origin master

popd


# check that new release branch exists, checkout/create
echo ${LINE}
echo "Create public@${NEW_RELEASE_NUM}"

pushd ${PUBLIC_REPO_PATH}

if [ -z "`git branch --list ${NEW_RELEASE_NUM}`" ]
then
   echo "'-public' branch ${NEW_RELEASE_NUM} doesn't exist. Creating branch."
   git checkout -b ${NEW_RELEASE_NUM}
else
   git checkout ${NEW_RELEASE_NUM}
fi


# copy files from dev release to public branch
echo ${LINE}
echo "Copy files from -private to -public repo"

find ${PRIVATE_REPO_PATH}/contraxsuite_services/ -name "*pyc" -delete

# copy only .txt files from /deploy folder
rsync -av ${PRIVATE_REPO_PATH}/contraxsuite_services/deploy/base/ \
          ${PUBLIC_REPO_PATH}/contraxsuite_services/deploy/base \
          --delete \
          --include="*.txt" \
          --exclude="*"
# copy all from /apps
rsync -av ${PRIVATE_REPO_PATH}/contraxsuite_services/apps/ \
          ${PUBLIC_REPO_PATH}/contraxsuite_services/apps \
          --delete
# copy all from /templates
rsync -av ${PRIVATE_REPO_PATH}/contraxsuite_services/templates/ \
          ${PUBLIC_REPO_PATH}/contraxsuite_services/templates \
          --delete
# copy all from /tests
rsync -av ${PRIVATE_REPO_PATH}/contraxsuite_services/tests/ \
          ${PUBLIC_REPO_PATH}/contraxsuite_services/tests \
          --delete
# copy /fixtures except /private
rsync -av ${PRIVATE_REPO_PATH}/contraxsuite_services/fixtures/ \
          ${PUBLIC_REPO_PATH}/contraxsuite_services/fixtures \
          --exclude private \
          --delete
# copy jars
rsync -av ${PRIVATE_REPO_PATH}/contraxsuite_services/jars/ \
          ${PUBLIC_REPO_PATH}/contraxsuite_services/jars \
          --delete
# copy utils
rsync -av ${PRIVATE_REPO_PATH}/contraxsuite_services/util/ \
          ${PUBLIC_REPO_PATH}/contraxsuite_services/util \
          --delete
# copy all from /documentation
rsync -av ${PRIVATE_REPO_PATH}/documentation/ \
          ${PUBLIC_REPO_PATH}/documentation \
          --delete
# copy all from /sdk
rsync -av ${PRIVATE_REPO_PATH}/sdk/ \
          ${PUBLIC_REPO_PATH}/sdk \
          --delete
# copy all from /sdk
rsync -av ${PRIVATE_REPO_PATH}/terraform/ \
          ${PUBLIC_REPO_PATH}/terraform \
          --delete
# copy /docker folder except local and private folders
rsync -av ${PRIVATE_REPO_PATH}/docker/ \
          ${PUBLIC_REPO_PATH}/docker \
          --exclude="deploy-private" \
          --exclude=".idea" \
          --exclude="setenv_local.sh" \
          --exclude="deploy/temp" \
          --delete
# copy /docker/deploy/dependencies folder except any zip
rsync -av ${PRIVATE_REPO_PATH}/docker/deploy/dependencies \
          ${PUBLIC_REPO_PATH}/docker/deploy/dependencies \
          --include="*.md" \
          --exclude="*" \
          --delete
# copy scripts
rsync -av ${PRIVATE_REPO_PATH}/scripts/ \
          ${PUBLIC_REPO_PATH}/scripts \
          --delete
# copy static files except theme and vendor
rsync -av ${PRIVATE_REPO_PATH}/static/ \
          ${PUBLIC_REPO_PATH}/static \
          --exclude theme \
          --exclude vendor \
          --delete
# copy files from root folder: .py, .sh, .pylintrc, .flake8, .example, except local_settings.py
rsync -av ${PRIVATE_REPO_PATH}/contraxsuite_services/ \
          ${PUBLIC_REPO_PATH}/contraxsuite_services \
          --include="*.py" \
          --include="*.sh" \
          --include="*.example" \
          --include=".pylintrc" \
          --include="*.flake8" \
          --exclude="*" \
          --exclude="local_settings.py" \
          --delete

cp -f ${PRIVATE_REPO_PATH}/version.txt ${PUBLIC_REPO_PATH}
cp -f ${PRIVATE_REPO_PATH}/README.md ${PUBLIC_REPO_PATH}

# create commit and push
echo ${LINE}
echo "Commit and push new ${NEW_RELEASE_NUM} branch to -public remote repo"
#git add --all
#git commit -m "${NEW_RELEASE_NUM} release initial commit"
#git push origin ${NEW_RELEASE_NUM}

# update public master
echo ${LINE}
echo "Update master branch in -public remote repo"
#git checkout master
#git pull origin master
#git merge ${NEW_RELEASE_NUM}
#git push origin master

popd
