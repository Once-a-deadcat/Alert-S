from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import os

# Azure Table Storage の接続文字列
connection_string = os.environ["CONNECTION_STRING"]

# テーブルサービスクライアントの作成
table_service_client = TableServiceClient.from_connection_string(connection_string)


async def get_tasks(user_id):
    # 新しいテーブルを作成する
    table_name = "tasks"

    try:
        table_service_client.create_table(table_name)
        print(f"Table '{table_name}' created successfully.")
    except ResourceExistsError:
        print(f"Table '{table_name}' already exists.")
        pass

    table_client = table_service_client.get_table_client(table_name)
    # エンティティを取得する
    filter = f"PartitionKey eq 'tasks-{user_id}'"
    entities = list(table_client.query_entities(query_filter=filter))
    print("Retrieved Entities:")
    print(entities)

    return entities


async def create_tasks(user_id, task_title, task_detail, task_status, task_color):
    # 新しいテーブルを作成する
    table_name = f"tasks"

    try:
        table_service_client.create_table(table_name)
        print(f"Table '{table_name}' created successfully.")
    except ResourceExistsError:
        print(f"Table '{table_name}' already exists.")

    tasks = await get_tasks(user_id=user_id)
    taskId = len(tasks) + 1
    # エンティティを追加する
    entity = {
        "PartitionKey": f"tasks-{user_id}",
        "RowKey": f"{taskId}",
        "TaskTitle": task_title,
        "TaskDetail": task_detail,
        "TaskStatus": task_status,
        "TaskColor": task_color,
    }

    table_client = table_service_client.get_table_client(table_name)
    table_client.upsert_entity(entity)
    print("Entity added successfully.")

    # エンティティを取得する
    retrieved_entity = table_client.get_entity(
        partition_key=f"tasks-{user_id}", row_key=f"{taskId}"
    )
    print("Retrieved Entity:")
    print(retrieved_entity)

    return retrieved_entity


async def update_tasks(user_id, task_id, task_status):
    # テーブル名の指定
    table_name = "tasks"

    # テーブルクライアントの生成
    table_client = table_service_client.get_table_client(table_name)

    # エンティティの取得
    try:
        entity = table_client.get_entity(
            partition_key=f"tasks-{user_id}", row_key=task_id
        )
    except ResourceNotFoundError:
        print(f"Task '{task_id}' not found.")
        return

    # ステータスの更新
    entity["TaskStatus"] = task_status

    # エンティティの更新
    table_client.update_entity(entity, mode=UpdateMode.REPLACE)

    print(f"Task '{task_id}' updated successfully.")

    # 更新されたエンティティの取得
    updated_entity = table_client.get_entity(
        partition_key=f"tasks-{user_id}", row_key=task_id
    )

    return updated_entity


async def delete_tasks(user_id, task_id):
    # テーブル名の指定
    table_name = "tasks"

    # テーブルクライアントの生成
    table_client = table_service_client.get_table_client(table_name)

    try:
        delete_task = table_client.get_entity(
            partition_key=f"tasks-{user_id}", row_key=task_id
        )
    except ResourceNotFoundError:
        print(f"Task '{task_id}' not found.")
        return

    # エンティティの削除
    table_client.delete_entity(partition_key=f"tasks-{user_id}", row_key=task_id)

    print(f"Task '{task_id}' deleted successfully.")

    return delete_task
