# Switchbot Alert on My Desk

## About This Bot

This DiscordBot supports sending alert signals to Switchbot items on your desk.
You can send an alert to the Switchbot owner set in this environment.
The user should describe the urgency level and details.

**priority rule**

・red >> yellow >> blue

・Registered early

## Command list (on discord)

Below are the main commands for the Task Manager Bot.


### Task Get Command

```bash
/get
```
The above command gets your task list.


### Task Get Command for Other Members

```bash
/get_member_tasks "target user id"
```

The above command gets the task list of another member. The "target user id" specifies the ID of the user whose task list is to be acquired.


### Complete Task Get Command

```bash
/done
```
The above command gets your task list.


### Complete Task Get Command for Other Members

```bash
/done_member_tasks "target user id"
```

The above command gets the completed task list of another member. The "target user id" specifies the ID of the user whose task list is to be acquired.


### Task Create Command

```bash
/create "task title" "task detail" "task color"
```

The above command creates a task. Specify the task's title, detail, and color in "task title", "task detail", "task color" respectively.

### Task Creation Command for Other Members

```bash
/create_member_task "task title" "task detail" "task color" "target user id"
```

The above command creates a task for another member. The "target user id" specifies the ID of the user for whom the task is being created.

### Task Update Command

```bash
/update "task id" "task status"
```

The above command updates the status of a task. Specify the ID of the task to be updated in "task id" and the new status in "task status".

### Task Deletion Command

```bash
/delete "task id"
```

The above command deletes a task. Specify the ID of the task to be deleted in "task id".

### Command to Delete Tasks of Other Members

```bash
/delete_member_task "target user id" "task id"
```

The above command deletes a task of another member. The "target user id" specifies the ID of the user whose task is to be deleted.


## For development

.env.sample

```bash
# Switchbot environment
API_KEY=
CLIENT_SECRET=
LED_DEVICE_ID=

# Discord environment
DISCORD_TOKEN=

# Azure Blob Storage environment
CONNECTION_STRING=
CONTAINER_NAME=

```

./deploy-sample.sh
```bash
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

```

If you want to run the script, do the following Run.

```bash

docker-compose up --build
```

thank you reading🍵
