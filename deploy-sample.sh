#!/bin/bash

# get current timestamp
timestamp=$(date +%Y%m%d%H%M%S)

# .env fileを読み込む
export $(egrep -v '^#' .env | xargs)

# ACRにログイン
docker login acrname.azurecr.io -u acruser -p password

# Timestamp有りでDockerビルドコマンドを実行
docker image build -t alert-s-switchbot:$timestamp .

# ACRにプッシュ
docker tag alert-s-switchbot:$timestamp acrname.azurecr.io/alert-s:$timestamp
docker push acrname.azurecr.io/alert-s:$timestamp

# bashからazコマンドを実行するためにログイン
az login
# コンテナ作る🍵
az container create \
  --resource-group rg \
  --name container \
  --image acrname.azurecr.io/alert-s:$timestamp \
  --registry-username acruser \
  --registry-password password \
  --dns-name-label alerts \
  --cpu 0.1 \
  --memory 0.1 \
  --restart-policy Always \
  --secure-environment-variables \
    API_KEY="" \
    CLIENT_SECRET="" \
    DISCORD_TOKEN="" \
    CONNECTION_STRING="" \
    CONTAINER_NAME="" \
    LED_DEVICE_ID="" \
    DISCORD_USER_ID= \
