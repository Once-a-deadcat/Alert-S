import discord
import os
import json
from switchbot.SwitchbotFunc import get_device_list
from lib.logger import AzureBlobHandler
import logging

# Configure logger settings
CONNECTION_STRING = os.environ["CONNECTION_STRING"]
CONTAINER_NAME = os.environ["CONTAINER_NAME"]
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = AzureBlobHandler(connection_string=CONNECTION_STRING,container_name=CONTAINER_NAME, blob_name_prefix='log')
handler.setFormatter(formatter)
logger.addHandler(handler)

# インテントの生成
intents = discord.Intents.default()
intents.message_content = True

# クライアントの生成
client = discord.Client(intents=intents)

def format_device_list(device_data):
    device_list = device_data['body']['deviceList']
    formatted_list = []
    for device in device_list:
        cloud_service_status = device.get('enableCloudService', 'N/A')
        device_info = f"### deviceName: {device['deviceName']} \n\tdeviceId: {device['deviceId']} \n\thubDeviceId: {device['hubDeviceId']} \n\tenableCloudService: {cloud_service_status} \n\t Type: {device['deviceType']}"
        formatted_list.append(device_info)
    return '\n'.join(formatted_list)

# discordと接続した時に呼ばれる
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# メッセージを受信した時に呼ばれる
@client.event
async def on_message(message):
    # 自分のメッセージを無効
    if message.author == client.user:
        return

    # メッセージが"$hello"で始まっていたら"Hello!"と応答
    if message.content.startswith('$hello'):
        logger.info("Hello! command received")
        await message.channel.send('Hello!')

    if message.content.startswith('$list'):
        device_list = await get_device_list()
        formatted_list = format_device_list(device_list)
        logger.info(f"list command received")
        logger.info(f"device list: {formatted_list}")
        await message.channel.send(formatted_list)
    
# クライアントの実行
token = os.environ['DISCORD_TOKEN']
client.run(token)
