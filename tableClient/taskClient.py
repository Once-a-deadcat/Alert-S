from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError
import os

# Azure Table Storage の接続文字列
connection_string = os.environ["CONNECTION_STRING"]

# テーブルサービスクライアントの作成
table_service_client = TableServiceClient.from_connection_string(connection_string)


async def get_tasks():
    # 新しいテーブルを作成する
    table_name = "tasks"

    try:
        table_service_client.create_table(table_name)
        print(f"Table '{table_name}' created successfully.")
    except ResourceExistsError:
        print(f"Table '{table_name}' already exists.")

    table_client = table_service_client.get_table_client(table_name)
    # エンティティを取得する
    filter = "PartitionKey eq 'tasks'"
    entities = list(table_client.query_entities(query_filter=filter))
    print("Retrieved Entities:")
    print(entities)

    return entities


async def create_tasks(task_title, task_detail, task_status, task_color):
    # 新しいテーブルを作成する
    table_name = "tasks"

    try:
        table_service_client.create_table(table_name)
        print(f"Table '{table_name}' created successfully.")
    except ResourceExistsError:
        print(f"Table '{table_name}' already exists.")

    tasks = await get_tasks()
    taskId = len(tasks) + 1
    # エンティティを追加する
    entity = {
        "PartitionKey": "tasks",
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
        partition_key="tasks", row_key=f"{taskId}"
    )
    print("Retrieved Entity:")
    print(retrieved_entity)

    return retrieved_entity
