from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import os

# Azure Table Storage の接続文字列
connection_string = os.environ["CONNECTION_STRING"]

# テーブルサービスクライアントの作成
table_service_client = TableServiceClient.from_connection_string(connection_string)


async def get_state(user_id):
    # 新しいテーブルを作成する
    table_name = "state"

    try:
        table_service_client.create_table(table_name)
        print(f"Table '{table_name}' created successfully.")
    except ResourceExistsError:
        print(f"Table '{table_name}' already exists.")

    table_client = table_service_client.get_table_client(table_name)
    # エンティティを取得する
    filter = f"RowKey eq '{user_id}'"
    entities = list(table_client.query_entities(query_filter=filter))
    print("Retrieved Entities:")

    if len(entities) == 0:
        return entities

    print(entities)

    return entities


async def create_state(user_id, light_color):
    # 新しいテーブルを作成する
    table_name = f"state"

    try:
        table_service_client.create_table(table_name)
        print(f"Table '{table_name}' created successfully.")
    except ResourceExistsError:
        print(f"Table '{table_name}' already exists.")

    state = await get_state(user_id=user_id)

    if len(state) == 0:
        # エンティティを追加する
        entity = {
            "PartitionKey": f"state",
            "RowKey": f"{user_id}",
            "LightState": light_color,
        }

        table_client = table_service_client.get_table_client(table_name)
        table_client.upsert_entity(entity)
        print("Entity added successfully.")
    else:
        return state

    # エンティティを取得する
    retrieved_entity = table_client.get_entity(
        partition_key=f"state", row_key=f"{user_id}"
    )
    print("Retrieved Entity:")
    print(retrieved_entity)

    return retrieved_entity


async def update_state(user_id, light_color):
    # テーブル名の指定
    table_name = "state"

    # テーブルクライアントの生成
    table_client = table_service_client.get_table_client(table_name)

    # エンティティの取得
    entity = table_client.get_entity(partition_key=f"state", row_key=user_id)

    # ステータスの更新
    entity["LightState"] = light_color

    # エンティティの更新
    table_client.update_entity(entity, mode=UpdateMode.REPLACE)

    print(f"state '{user_id}' updated successfully.")

    # 更新されたエンティティの取得
    updated_entity = table_client.get_entity(partition_key=f"state", row_key=user_id)

    return updated_entity
