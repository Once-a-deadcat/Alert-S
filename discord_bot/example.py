import discord
import os
import json
from switchbot.SwitchbotFunc import get_device_list

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
        await message.channel.send('Hello!')

    if message.content.startswith('$list'):
        device_list = await get_device_list()
        formatted_list = format_device_list(device_list)
        await message.channel.send(formatted_list)
    
# クライアントの実行
token = os.environ['DISCORD_TOKEN']
client.run(token)
