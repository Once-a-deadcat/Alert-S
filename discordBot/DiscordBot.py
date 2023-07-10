import asyncio
import discord
import os
import json
from switchBot.SwitchbotFunc import get_device_list, set_light_color
from lib.logger import AzureBlobHandler
import logging
from tableClient.taskClient import get_tasks, create_tasks, update_tasks, delete_tasks
from tableClient.stateClient import get_state, create_state, update_state
from discord import (
    Guild,
    app_commands,
    Interaction,
    SelectOption,
    TextInput,
    User,
    Member,
    Embed,
)
from discord.ui import Select, Button, View, UserSelect
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
intents.members = True
intents = discord.Intents.all()

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


# slash commandを受信した時に呼ばれる
@tree.command(name="list", description="デバイスリストを返してくれます")
async def list(interaction: discord.Interaction):
    logger.info("/list command received")

    device_list = await get_device_list()
    formatted_list = format_device_list(device_list)
    logger.info(f"list command received")
    await interaction.response.send_message(formatted_list, ephemeral=False)


async def update_color(user_id: int):
    DISCORD_USER_ID = int(os.environ["DISCORD_USER_ID"])
    if user_id != DISCORD_USER_ID:
        return

    tasks = await get_tasks(user_id=user_id, server_id=0)

    # set default light_color
    light_color = "NONE"

    if len(tasks) > 0:
        for task in tasks:
            if task["TaskStatus"].upper() != "COMPLETED":
                if task["TaskColor"] == "RED":
                    light_color = "RED"
                    await set_light_color(light_color)
                    # await update_state(user_id, light_color)
                    break  # As RED is the highest priority, we can break the loop when we find it.
                elif task["TaskColor"] == "YELLOW":
                    light_color = "YELLOW"  # If we later find a RED task, this will be overwritten.
                elif task["TaskColor"] == "BLUE" and light_color == "NONE":
                    light_color = (
                        "BLUE"  # BLUE is only set if no RED or YELLOW tasks are found.
                    )
            else:
                pass  # If the task is completed, we don't need to do anything.

    # Update the color only once after checking all tasks
    await set_light_color(light_color)
    # await update_state(user_id, light_color)

    return light_color


@tree.command(name="get", description="Job一覧を返してくれます")
async def get(interaction: discord.Interaction):
    logger.info("/get command received")

    user_id = interaction.user.id
    server_id = interaction.guild.id  # Get the server ID

    tasks = await get_tasks(user_id, server_id)

    if len(tasks) == 0:
        await interaction.response.send_message("No tasks found.", ephemeral=True)
        return

    # Markdown text generation
    markdown_texts = ""
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
            active_flag = False
            markdown_text += f"### Color:  {color}\n"

            for task in tasks_in_color:
                if task["TaskStatus"].upper() != "COMPLETED":
                    markdown_text += f'- TaskId:  {task["TaskId"]}  /  Status:  {task["TaskStatus"]}\n'
                    markdown_text += f'\tTitle:  {task["TaskTitle"]}\n'
                    markdown_text += f'\tDetail: {task["TaskDetail"]}\n'
                    active_flag = True

            if active_flag:
                markdown_texts += markdown_text
                markdown_text = ""
            else:
                markdown_text = ""

    if markdown_texts == "":
        markdown_texts = "No tasks found."

    await interaction.response.send_message(markdown_texts, ephemeral=True)


async def member_options(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    data = []
    members = interaction.guild.members
    for member in members:
        if not member.bot:
            if member.nick is not None:
                data.append(
                    app_commands.Choice(name=str(member.nick), value=str(member.id))
                )
            else:
                data.append(
                    app_commands.Choice(name=str(member.name), value=str(member.id))
                )
    return data


@tree.command(name="done", description="完了したJob一覧を返してくれます")
async def done(interaction: discord.Interaction):
    logger.info("/done command received")

    user_id = interaction.user.id
    server_id = interaction.guild.id  # Get the server ID

    tasks = await get_tasks(user_id, server_id)

    if len(tasks) == 0:
        await interaction.response.send_message("No tasks found.", ephemeral=True)
        return

    # Markdown text generation
    markdown_texts = ""
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
            active_flag = False
            markdown_text += f"### Color:  {color}\n"

            for task in tasks_in_color:
                if task["TaskStatus"].upper() == "COMPLETED":
                    markdown_text += f'- TaskId:  {task["TaskId"]}  /  Status:  {task["TaskStatus"]}\n'
                    markdown_text += f'\tTitle: {task["TaskTitle"]}\n'
                    markdown_text += f'\tDetail: {task["TaskDetail"]}\n'
                    active_flag = True

            if active_flag:
                markdown_texts += markdown_text
                markdown_text = ""
            else:
                markdown_text = ""

    if markdown_texts == "":
        markdown_texts = "No tasks found."

    await interaction.response.send_message(markdown_texts, ephemeral=True)


@tree.command(name="get_all_tasks", description="全サーバーでのJob一覧を返してくれます")
async def get(interaction: discord.Interaction):
    logger.info("/get command received")

    user_id = interaction.user.id
    # server_id = interaction.guild.id  # Get the server ID
    server_id = 0

    tasks = await get_tasks(user_id, server_id)

    if len(tasks) == 0:
        await interaction.response.send_message("No tasks found.", ephemeral=False)
        return

    # Markdown text generation
    markdown_texts = ""
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
            active_flag = False
            markdown_text += f"### Color:  {color}\n"

            for task in tasks_in_color:
                if task["TaskStatus"].upper() != "COMPLETED":
                    markdown_text += f'- TaskId:  {task["TaskId"]}  /  Status:  {task["TaskStatus"]}\n'
                    markdown_text += f'\tTitle:  {task["TaskTitle"]}\n'
                    markdown_text += f'\tDetail: {task["TaskDetail"]}\n'
                    active_flag = True

            if active_flag:
                markdown_texts += markdown_text
                markdown_text = ""
            else:
                markdown_text = ""

    if markdown_texts == "":
        markdown_texts = "No tasks found."

    await interaction.response.send_message(markdown_texts, ephemeral=True)


@tree.command(name="done_all_tasks", description="完了した全サーバーでのJob一覧を返してくれます")
async def get(interaction: discord.Interaction):
    logger.info("/get command received")

    user_id = interaction.user.id
    # server_id = interaction.guild.id  # Get the server ID
    server_id = 0

    tasks = await get_tasks(user_id, server_id)

    if len(tasks) == 0:
        await interaction.response.send_message("No tasks found.", ephemeral=True)
        return

    # Markdown text generation
    markdown_texts = ""
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
            active_flag = False
            markdown_text += f"### Color:  {color}\n"

            for task in tasks_in_color:
                if task["TaskStatus"].upper() == "COMPLETED":
                    markdown_text += f'- TaskId:  {task["TaskId"]}  /  Status:  {task["TaskStatus"]}\n'
                    markdown_text += f'\tTitle:  {task["TaskTitle"]}\n'
                    markdown_text += f'\tDetail: {task["TaskDetail"]}\n'
                    active_flag = True

            if active_flag:
                markdown_texts += markdown_text
                markdown_text = ""
            else:
                markdown_text = ""

    if markdown_texts == "":
        markdown_texts = "No tasks found."

    await interaction.response.send_message(markdown_texts, ephemeral=True)


@tree.command(name="get_member_tasks", description="Job一覧を返します(指定したユーザー)")
@app_commands.autocomplete(target_user_id=member_options)
async def get_member_tasks(interaction: discord.Interaction, target_user_id: str):
    # target_user = client.get_user(int(target_user_id))
    server_id = interaction.guild.id  # Get the server ID
    tasks = await get_tasks(
        target_user_id, server_id
    )  # assuming get_tasks accepts a user_id
    # Markdown text generation
    markdown_texts = ""
    members = interaction.guild.members

    for member in members:
        if member.id == int(target_user_id):
            if member.nick is not None:
                name = member.nick
            else:
                name = member.name
    markdown_text = f"### User: {name}\n"  # Grouping tasks by color
    if len(tasks) == 0:
        markdown_text += "No tasks found.\n"
        await interaction.response.send_message(markdown_text, ephemeral=True)
        return
    tasks_by_color = dict()
    for task in tasks:
        color = task["TaskColor"].upper()  # Unify the color representation
        if color not in tasks_by_color:
            tasks_by_color[color] = []
        tasks_by_color[color].append(task)

    # Order of colors
    color_order = ["RED", "YELLOW", "BLUE"]
    markdown_texts += markdown_text
    markdown_text = ""

    # Generating markdown for each color in the specified order
    for color in color_order:
        if color in tasks_by_color:
            tasks_in_color = tasks_by_color[color]
            active_flag = False
            markdown_text += f"### Color:  {color}\n"

            for task in tasks_in_color:
                if task["TaskStatus"].upper() != "COMPLETED":
                    markdown_text += f'- TaskId:  {task["TaskId"]}  /  Status:  {task["TaskStatus"]}\n'
                    markdown_text += f'\tTitle:  {task["TaskTitle"]}\n'
                    markdown_text += f'\tDetail: {task["TaskDetail"]}\n'
                    active_flag = True

            if active_flag:
                markdown_texts += markdown_text
                markdown_text = ""
            else:
                markdown_text = ""

    if markdown_texts == "":
        markdown_texts = "No tasks found."

    await interaction.response.send_message(markdown_texts, ephemeral=False)


@tree.command(name="done_member_tasks", description="完了したJob一覧を返します(指定したユーザー)")
@app_commands.autocomplete(target_user_id=member_options)
async def done_member_tasks(interaction: discord.Interaction, target_user_id: str):
    # target_user = client.get_user(int(target_user_id))
    server_id = interaction.guild.id  # Get the server ID
    tasks = await get_tasks(
        target_user_id, server_id
    )  # assuming get_tasks accepts a user_id
    # Markdown text generation
    markdown_texts = ""
    members = interaction.guild.members

    for member in members:
        if member.id == int(target_user_id):
            if member.nick is not None:
                name = member.nick
            else:
                name = member.name
    markdown_text = f"### User: {name}\n"  # Grouping tasks by color
    if len(tasks) == 0:
        markdown_text += "No tasks found.\n"
        await interaction.response.send_message(markdown_text, ephemeral=True)
        return
    tasks_by_color = dict()
    for task in tasks:
        color = task["TaskColor"].upper()  # Unify the color representation
        if color not in tasks_by_color:
            tasks_by_color[color] = []
        tasks_by_color[color].append(task)

    # Order of colors
    color_order = ["RED", "YELLOW", "BLUE"]
    markdown_texts += markdown_text
    markdown_text = ""

    # Generating markdown for each color in the specified order
    for color in color_order:
        if color in tasks_by_color:
            tasks_in_color = tasks_by_color[color]
            active_flag = False
            markdown_text += f"### Color:  {color}\n"

            for task in tasks_in_color:
                if task["TaskStatus"].upper() == "COMPLETED":
                    markdown_text += f'- TaskId:  {task["TaskId"]}  /  Status:  {task["TaskStatus"]}\n'
                    markdown_text += f'\tTitle:  {task["TaskTitle"]}\n'
                    markdown_text += f'\tDetail: {task["TaskDetail"]}\n'
                    active_flag = True

            if active_flag:
                markdown_texts += markdown_text
                markdown_text = ""
            else:
                markdown_text = ""

    if markdown_texts == "":
        markdown_texts = "No tasks found."

    await interaction.response.send_message(markdown_texts, ephemeral=False)


async def task_color_options(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    data = []
    colors = ["RED", "YELLOW", "BLUE"]
    for color_choice in colors:
        if current.lower() in color_choice.lower():
            data.append(app_commands.Choice(name=color_choice, value=color_choice))
    return data


@tree.command(name="create", description="Jobを作成してくれます")
@app_commands.autocomplete(
    task_color=task_color_options,
)
async def create(
    interaction: discord.Interaction, task_title: str, task_detail: str, task_color: str
):
    await interaction.response.defer()
    colors = ["RED", "YELLOW", "BLUE"]  # Available color choices
    task_color = task_color.upper()
    if task_color not in colors:
        await interaction.followup.send(
            "Invalid color. Please choose from RED, YELLOW, or BLUE.", ephemeral=True
        )
    else:
        user_id = interaction.user.id
        server_id = interaction.guild.id  # Get the server ID
        task_status = "NOT TOUCHED"
        created_task = await create_tasks(
            user_id, server_id, task_title, task_detail, task_status, task_color
        )
        await update_color(user_id)
        # await create_state(user_id, created_task["TaskColor"])
        logger.info(f"create command received")
        logger.info(f"created task: {created_task}")
        markdown_text = f"### Color:  {created_task['TaskColor']}\n"
        markdown_text += f'- TaskId:  {created_task["TaskId"]}  /  Status:  {created_task["TaskStatus"]}\n'
        markdown_text += f'\tTitle:  {created_task["TaskTitle"]}\n'
        markdown_text += f'\tDetail: {created_task["TaskDetail"]}\n'
        markdown_text += f"### Jobが作成されました.\n"
        await interaction.followup.send(markdown_text, ephemeral=False)


@tree.command(name="create_member_task", description="Jobを作成してくれます")
@app_commands.autocomplete(
    task_color=task_color_options,
    target_user_id=member_options,
)
async def create_member_task(
    interaction: discord.Interaction,
    task_title: str,
    task_detail: str,
    task_color: str,
    target_user_id: str,
):
    await interaction.response.defer()
    colors = ["RED", "YELLOW", "BLUE"]  # Available color choices
    task_color = task_color.upper()
    if task_color not in colors:
        await interaction.followup.send(
            "Invalid color. Please choose from RED, YELLOW, or BLUE.", ephemeral=True
        )
    else:
        user_id = target_user_id
        server_id = interaction.guild.id  # Get the server ID

        task_status = "NOT TOUCHED"
        created_task = await create_tasks(
            user_id, server_id, task_title, task_detail, task_status, task_color
        )
        await update_color(int(user_id))
        # await create_state(user_id, created_task["TaskColor"])
        logger.info(f"create command received")
        logger.info(f"created task: {created_task}")
        markdown_text = f"### Color:  {created_task['TaskColor']}\n"
        markdown_text += f'- TaskId:  {created_task["TaskId"]}  /  Status:  {created_task["TaskStatus"]}\n'
        markdown_text += f'\tTitle:  {created_task["TaskTitle"]}\n'
        markdown_text += f'\tDetail: {created_task["TaskDetail"]}\n'
        markdown_text += f"### Jobが作成されました.\n"
        # Add mention to the user
        markdown_text += f"<@{user_id}> Job has been assigned to you🔫\n"
        await interaction.followup.send(markdown_text, ephemeral=False)


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
    server_id = interaction.guild.id  # Get the server ID

    tasks = await get_tasks(user_id, server_id)
    for task in tasks:
        choice = f'・TaskId:  {task["TaskId"]}  /  Title:  {task["TaskTitle"]}  /  Status:  {task["TaskStatus"]}  /  Color:  {task["TaskColor"]}\n'
        data.append(app_commands.Choice(name=choice, value=task["TaskId"]))
    return data


@tree.command(name="update", description="Jobのステータスを更新してくれます")
@app_commands.autocomplete(task_id=task_id_options, task_status=task_status_options)
async def update(interaction: discord.Interaction, task_id: str, task_status: str):
    await interaction.response.defer(ephemeral=True)
    user_id = interaction.user.id
    server_id = interaction.guild.id  # Get the server ID

    created_task = await update_tasks(user_id, server_id, task_id, task_status)
    if created_task is None:
        await interaction.followup.send("Task not found.", ephemeral=True)
        return
    color = await update_color(user_id)
    logger.info(f"update_tasks command received")
    logger.info(f"update_tasks task: {created_task}")
    markdown_text = f"### Color:  {created_task['TaskColor']}\n"
    markdown_text += f'- TaskId:  {created_task["TaskId"]}  /  Status:  {created_task["TaskStatus"]}\n'
    markdown_text += f'\tTitle:  {created_task["TaskTitle"]}\n'
    markdown_text += f'\tDetail: {created_task["TaskDetail"]}\n'
    markdown_text += f"### Jobの状態が更新されました.\n"
    await interaction.followup.send(markdown_text, ephemeral=True)


@tree.command(name="delete", description="Jobを削除してくれます")
@app_commands.autocomplete(task_id=task_id_options)
async def delete(interaction: discord.Interaction, task_id: str):
    await interaction.response.defer(ephemeral=True)
    user_id = interaction.user.id
    server_id = interaction.guild.id  # Get the server ID

    deleted_task = await delete_tasks(user_id, server_id, task_id)
    if deleted_task is None:
        await interaction.followup.send("Task not found.", ephemeral=True)
        return
    await update_color(user_id)
    logger.info(f"delete_tasks command received")
    logger.info(f"delete_tasks task: {deleted_task}")
    markdown_text = f"### Color:  {deleted_task['TaskColor']}\n"
    markdown_text += f'- TaskId:  {deleted_task["TaskId"]}  /  Status:  {deleted_task["TaskStatus"]}\n'
    markdown_text += f'\tTitle:  {deleted_task["TaskTitle"]}\n'
    markdown_text += f'\tDetail: {deleted_task["TaskDetail"]}\n'
    markdown_text += f"### Jobが削除されました.\n"
    await interaction.followup.send(markdown_text, ephemeral=True)


async def task_id_options_by_userid(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    data = []
    user_id = interaction.data["options"][0][
        "value"
    ]  # assuming the user_id is the first option
    server_id = interaction.guild.id  # Get the server ID

    tasks = await get_tasks(user_id, server_id)
    for task in tasks:
        choice = f'・TaskId:  {task["TaskId"]}  /  Title:  {task["TaskTitle"]}  /  Status:  {task["TaskStatus"]}  /  Color:  {task["TaskColor"]}\n'
        data.append(app_commands.Choice(name=choice, value=task["TaskId"]))
    return data


@tree.command(name="delete_member_task", description="Jobを削除してくれます")
@app_commands.autocomplete(
    target_user_id=member_options,
    task_id=task_id_options_by_userid,
)
async def delete_member_task(
    interaction: discord.Interaction, target_user_id: str, task_id: str
):
    await interaction.response.defer()
    user_id = target_user_id
    server_id = interaction.guild.id  # Get the server ID

    # task select by user_id
    deleted_task = await delete_tasks(user_id, server_id, task_id)
    if deleted_task is None:
        await interaction.followup.send("Task not found.", ephemeral=False)
        return
    await update_color(int(user_id))
    logger.info(f"delete_tasks command received")
    logger.info(f"delete_tasks task: {deleted_task}")
    markdown_text = f"### Color:  {deleted_task['TaskColor']}\n"
    markdown_text += f'- TaskId:  {deleted_task["TaskId"]}  /  Status:  {deleted_task["TaskStatus"]}\n'
    markdown_text += f'\tTitle:  {deleted_task["TaskTitle"]}\n'
    markdown_text += f'\tDetail: {deleted_task["TaskDetail"]}\n'
    markdown_text += f"### Jobが削除されました.\n"
    # Add mention to the user
    markdown_text += f"<@{user_id}> Job has been assigned to you🔫\n"
    await interaction.followup.send(markdown_text, ephemeral=False)


@tree.command(name="light", description="指定の色に光らせます")
@app_commands.autocomplete(
    color=task_color_options,
)
async def light(interaction: discord.Interaction, color: str):
    colors = ["RED", "YELLOW", "BLUE"]  # Available color choices
    task_color = color.upper()
    if task_color not in colors:
        await interaction.followup.send(
            "Invalid color. Please choose from RED, YELLOW, or BLUE.", ephemeral=True
        )
    else:
        DISCORD_USER_ID = int(os.environ["DISCORD_USER_ID"])
        await interaction.response.defer()
        logger.info("Setting light color to red...")
        user_id = interaction.user.id
        if user_id == DISCORD_USER_ID:
            await set_light_color(color)
            logger.info("Light color set to red")
            await interaction.followup.send(f"{color} に光らせました!!")
        else:
            await interaction.followup.send(f"あなたはこのコマンドを実行できません")


# メッセージを受信した時に呼ばれる
@client.event
async def on_message(message):
    # 自分のメッセージを無効
    if message.author == client.user:
        await tree.sync()  # スラッシュコマンドを同期
        return


# クライアントの実行
token = os.environ["DISCORD_TOKEN"]
client.run(token)
