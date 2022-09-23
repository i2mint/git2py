#!/bin/bash

GITLAB_URL=$1
GITHUB_ORG=$2

migrate_repository () {
    GITLAB_USERNAME=$1
    REPOSITORY_NAME=$2

    git clone --mirror $GITLAB_URL/$GITLAB_USERNAME/$REPOSITORY_NAME.git
    cd $REPOSITORY_NAME.git
    git push --no-verify --mirror https://github.com/$GITHUB_ORG/$REPOSITORY_NAME.git
}

