#!/bin/bash

# get current timestamp
timestamp=$(date +%Y%m%d%H%M%S)

# ACRにログイン
docker login imagename.azurecr.io -u username -p password

# Dockerビルドコマンドを実行
docker image build -t imagename:$timestamp .

docker tag imagename:$timestamp imagename.azurecr.io/imagename:$timestamp
docker push imagename.azurecr.io/imagename:$timestamp

az login
# Create or update the container instance
az container create \
  --resource-group rg-name \
  --name acrname \
  --image imagename.azurecr.io/imagename:$timestamp \
  --registry-username username \
  --registry-password password \
  --dns-name-label alerts \
  --restart-policy Always \
  --secure-environment-variables \
    API_KEY= \
    CLIENT_SECRET= \
    DISCORD_TOKEN= \
    CONNECTION_STRING= \
    CONTAINER_NAME=
