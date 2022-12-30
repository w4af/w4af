#!/bin/bash

# This script builds and officially releases Docker image from source. Use it only
# if you're project maintainer.

set -x
set -e

cp Dockerfile ../../
cp .dockerignore ../../

cd ../../


if [ $# -eq 1 ]; then
    ENV=$1
else
    echo "Build environment name argument is required (./docker-build-release.sh develop)"
    exit 1
fi

docker-tag-naming bump andresriancho/w4af ${ENV} --commit-id ${CIRCLE_SHA1:0:7} > /tmp/new-w4af-docker-tag.txt
NEW_TAG=`cat /tmp/new-w4af-docker-tag.txt`

docker build -t andresriancho/w4af:${ENV} .
docker tag andresriancho/w4af:${ENV} andresriancho/w4af:${NEW_TAG}

docker push andresriancho/w4af:${ENV}
docker push andresriancho/w4af:${NEW_TAG}

rm -rf Dockerfile
rm -rf .dockerignore

cd extras/docker/

