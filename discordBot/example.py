import discord
import os
import json
from switchBot.SwitchbotFunc import get_device_list
from lib.logger import AzureBlobHandler
import logging
from tableClient.taskClient import get_tasks, create_tasks, update_tasks

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
    logger.info("/hello command received")
    reply_text = "Hello!"
    await interaction.response.send_message(reply_text, ephemeral=True)


# slash commandを受信した時に呼ばれる
@tree.command(name="list", description="デバイスリストを返してくれます")
async def hello(interaction: discord.Interaction):
    logger.info("/list command received")

    device_list = await get_device_list()
    formatted_list = format_device_list(device_list)
    logger.info(f"list command received")
    logger.info(f"device list: {formatted_list}")
    await interaction.response.send_message(formatted_list, ephemeral=False)


@tree.command(name="get", description="報告一覧を返してくれます")
async def hello(interaction: discord.Interaction):
    logger.info("/get command received")

    user_id = interaction.user.id
    tasks = await get_tasks(user_id)

    if len(tasks) == 0:
        await interaction.response.send_message("No tasks found.", ephemeral=False)
        return

    # Markdown text generation
    markdown_text = ""

    # Grouping tasks by color
    tasks_by_color = dict()
    for task in tasks:
        color = task["TaskColor"].upper()  # Unify the color representation
        if color not in tasks_by_color:
            tasks_by_color[color] = []
        tasks_by_color[color].append(task)

    # Order of colors
    color_order = ["RED", "YELLOW", "BLUE"]

    # Generating markdown for each color in the specified order
    for color in color_order:
        if color in tasks_by_color:
            tasks_in_color = tasks_by_color[color]
            markdown_text += f"### Color:  {color}\n"
            for task in tasks_in_color:
                if task["TaskStatus"].upper() != "COMPLETED":
                    markdown_text += f'・TaskId:  {task["RowKey"]}  /  Title:  {task["TaskTitle"]}  /  Status:  {task["TaskStatus"]}\n'
                    markdown_text += f'\t Detail: {task["TaskDetail"]}\n'

    await interaction.response.send_message(markdown_text, ephemeral=False)


@tree.command(name="get_user_tasks", description="指定したユーザーの報告一覧を返します")
async def hello(
    interaction: discord.Interaction,
    target_user: discord.User = app_commands.UserOption(description="指定したいユーザー"),
):
    tasks = await get_tasks(target_user.id)  # assuming get_tasks accepts a user_id
    # Markdown text generation
    markdown_text = f"### User: {target_user.name}\n"
    for task in tasks:
        markdown_text += f'・TaskId:  {task["RowKey"]}  /  Title:  {task["TaskTitle"]}  /  Status:  {task["TaskStatus"]}\n'
        markdown_text += f'\t Detail: {task["TaskDetail"]}\n'
    await interaction.response.send_message(markdown_text, ephemeral=False)


async def task_color_options(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    data = []
    colors = ["RED", "YELLOW", "BLUE"]
    for color_choice in colors:
        if current.lower() in color_choice.lower():
            data.append(app_commands.Choice(name=color_choice, value=color_choice))
    return data


@tree.command(name="create", description="報告を作成してくれます")
@app_commands.autocomplete(
    task_color=task_color_options,
)
async def hello(
    interaction: discord.Interaction, task_title: str, task_detail: str, task_color: str
):
    user_id = interaction.user.id
    task_status = "NOT TOUCHED"
    created_task = await create_tasks(
        user_id, task_title, task_detail, task_status, task_color
    )
    logger.info(f"create command received")
    logger.info(f"created task: {created_task}")
    markdown_text = f"### Color:  {created_task['TaskColor']}\n"
    markdown_text += f'・TaskId:  {created_task["RowKey"]}  /  Title:  {created_task["TaskTitle"]}  /  Status:  {created_task["TaskStatus"]}\n'
    markdown_text += f'\t Detail: {created_task["TaskDetail"]}\n'
    await interaction.response.send_message(markdown_text, ephemeral=False)


async def task_status_options(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    data = []
    colors = ["IN PROGRESS", "COMPLETED", "NOT TOUCHED"]
    for color_choice in colors:
        if current.lower() in color_choice.lower():
            data.append(app_commands.Choice(name=color_choice, value=color_choice))
    return data


async def task_id_options(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    data = []
    user_id = interaction.user.id
    tasks = await get_tasks(user_id)
    for task in tasks:
        if current.lower() in task["RowKey"].lower():
            choice = f'・TaskId:  {task["RowKey"]}  /  Title:  {task["TaskTitle"]}  /  Status:  {task["TaskStatus"]}\n'
            data.append(app_commands.Choice(name=task["RowKey"], value=choice))
    return data


@tree.command(name="update", description="報告のステータスを更新してくれます")
@app_commands.autocomplete(task_id=task_id_options, task_status=task_status_options)
async def hello(interaction: discord.Interaction, task_id: str, task_status: str):
    user_id = interaction.user.id
    created_task = await update_tasks(user_id, task_id, task_status)
    logger.info(f"update_tasks command received")
    logger.info(f"update_tasks task: {created_task}")
    markdown_text = f"### Color:  {created_task['TaskColor']}\n"
    markdown_text += f'・TaskId:  {created_task["RowKey"]}  /  Title:  {created_task["TaskTitle"]}  /  Status:  {created_task["TaskStatus"]}\n'
    markdown_text += f'\t Detail: {created_task["TaskDetail"]}\n'
    await interaction.response.send_message(markdown_text, ephemeral=False)


# メッセージを受信した時に呼ばれる
@client.event
async def on_message(message):
    # 自分のメッセージを無効
    if message.author == client.user:
        return


# クライアントの実行
token = os.environ["DISCORD_TOKEN"]
client.run(token)
