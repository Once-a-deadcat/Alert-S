import discord
import os
import json
from switchBot.SwitchbotFunc import get_device_list
from lib.logger import AzureBlobHandler
import logging
from tableClient.taskClient import get_tasks, create_tasks

from discord import (
    app_commands,
    Interaction,
    SelectOption,
    TextInput,
    User,
)
from discord.ui import Select, Button, View
from discord.ext import commands
from typing import List

# Configure logger settings
CONNECTION_STRING = os.environ["CONNECTION_STRING"]
CONTAINER_NAME = os.environ["CONTAINER_NAME"]
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = AzureBlobHandler(
    connection_string=CONNECTION_STRING,
    container_name=CONTAINER_NAME,
    blob_name_prefix="log",
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# インテントの生成
intents = discord.Intents.default()
intents.message_content = True

# クライアントの生成
client = discord.Client(intents=intents, command_prefix="/")
tree = app_commands.CommandTree(client)


# discordと接続した時に呼ばれる
@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await tree.sync()  # スラッシュコマンドを同期


def format_device_list(device_data):
    device_list = device_data["body"]["deviceList"]
    formatted_list = []
    for device in device_list:
        cloud_service_status = device.get("enableCloudService", "N/A")
        device_info = f"### deviceName: {device['deviceName']} \n\tdeviceId: {device['deviceId']} \n\thubDeviceId: {device['hubDeviceId']} \n\tenableCloudService: {cloud_service_status} \n\ttype: {device['deviceType']}"
        formatted_list.append(device_info)
    return "\n".join(formatted_list)


@tree.command(name="test", description="テストコマンドです。")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "てすと！", ephemeral=True
    )  # ephemeral=True→「これらはあなただけに表示されています」


# slash commandを受信した時に呼ばれる
@tree.command(name="hello", description="あいさつを返してくれます")
async def hello(interaction: discord.Interaction):
    logger.info("Hello! command received")
    reply_text = "Hello!"
    await interaction.response.send_message(reply_text, ephemeral=True)


# メッセージを受信した時に呼ばれる
@client.event
async def on_message(message):
    # 自分のメッセージを無効
    if message.author == client.user:
        return

    # メッセージが"$hello"で始まっていたら"Hello!"と応答
    if message.content.startswith("$hello"):
        logger.info("Hello! command received")
        await message.channel.send("Hello!")

    if message.content.startswith("$list"):
        device_list = await get_device_list()
        formatted_list = format_device_list(device_list)
        logger.info(f"list command received")
        logger.info(f"device list: {formatted_list}")
        await message.channel.send(formatted_list)

    if message.content.startswith("$get"):
        tasks = await get_tasks()
        logger.info(f"get command received")
        logger.info(f"tasks: {tasks}")
        await message.channel.send(tasks)

    if message.content.startswith("$create"):
        _, task_title, task_detail, task_status, task_color = message.content.split()
        created_task = await create_tasks(
            task_title, task_detail, task_status, task_color
        )
        logger.info(f"create command received")
        logger.info(f"created task: {created_task}")
        await message.channel.send(created_task)


# クライアントの実行
token = os.environ["DISCORD_TOKEN"]
client.run(token)
