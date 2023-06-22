# Switchbot Alert on My Desk

## About This Bot

This DiscordBot supports sending alert signals to Switchbot items on your desk.

## Command list (on discord)

### **/push {urgency level} {task details}**

You can send an alert to the Switchbot owner set in this environment.
The user should describe the urgency level and details.

**Options**

・urgency level: red || yellow || blue

・task details: About task description.

**priority rule**

・red >> yellow >> blue

・Registered early

### **/get**

Gets the list of tasks that have been set for the User.
They are grouped by urgency level and displayed in the order in which they were registered first.

## For development

.env.sample

```bash
API_KEY=""
CLIENT_SECRET=""
DISCORD_TOKEN=""
```

If you want to run the script, do the following Run.

```bash

docker-compose up --build
```

thank you reading…
