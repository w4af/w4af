#!/bin/bash

# This scripts builds Docker image from actual source code, so you can access it
# as andresriancho/w4af:source
# Use it if for any reasons you want to run w4af inside Docker

cp Dockerfile ../../
cp .dockerignore ../../

cd ../../

docker build -t andresriancho/w4af:source .

rm -rf Dockerfile
rm -rf .dockerignore

cd extras/docker/
