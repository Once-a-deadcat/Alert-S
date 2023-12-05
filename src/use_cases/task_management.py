# use_cases/task_management.py
from domain.task import Task
from infrastructure.azure_table import AzureTable

class TaskManagement:
    def __init__(self):
        self.azure_table = AzureTable()

    async def get_tasks(self, user_id, server_id):
        return self.azure_table.get_tasks(user_id, server_id)

    async def create_task(self, user_id, server_id, task_title, task_detail, task_status, task_color):
        tasks = self.azure_table.get_tasks(user_id, server_id)
        task_id = len(tasks) + 1
        task = Task(
            user_id=user_id, 
            server_id=server_id, 
            task_id=task_id, 
            task_title=task_title, 
            task_detail=task_detail, 
            task_status=task_status, 
            task_color=task_color
        )
        response = self.azure_table.create_task(task)
        return response

    async def update_task(self, user_id, server_id, task_id, task_status):
        response = self.azure_table.update_task(user_id, server_id, task_id, task_status)
        return response

    async def delete_task(self, user_id, server_id, task_id):
        response = self.azure_table.delete_task(user_id, server_id, task_id)
        return response


# ------ old code ------

# from azure.data.tables import TableServiceClient, UpdateMode
# from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
# import os

# # Azure Table Storage の接続文字列
# connection_string = os.environ["CONNECTION_STRING"]

# # テーブルサービスクライアントの作成
# table_service_client = TableServiceClient.from_connection_string(connection_string)


# async def get_tasks(user_id, server_id):
#     # 新しいテーブルを作成する
#     table_name = "tasks"

#     try:
#         table_service_client.create_table(table_name)
#         print(f"Table '{table_name}' created successfully.")
#     except ResourceExistsError:
#         print(f"Table '{table_name}' already exists.")
#         pass

#     table_client = table_service_client.get_table_client(table_name)
#     # エンティティを取得する
#     if server_id == 0:
#         filter = f"PartitionKey eq 'tasks-{user_id}'"
#         entities = list(table_client.query_entities(query_filter=filter))
#         print("Retrieved Entities:")
#         print(entities)
#         return entities
#     else:
#         filter = f"PartitionKey eq 'tasks-{user_id}' and ServerId eq '{server_id}'"
#         entities = list(table_client.query_entities(query_filter=filter))
#         print("Retrieved Entities:")
#         print(entities)
#         return entities


# async def create_tasks(
#     user_id, server_id, task_title, task_detail, task_status, task_color
# ):
#     # 新しいテーブルを作成する
#     table_name = f"tasks"

#     try:
#         table_service_client.create_table(table_name)
#         print(f"Table '{table_name}' created successfully.")
#     except ResourceExistsError:
#         print(f"Table '{table_name}' already exists.")

#     tasks = await get_tasks(user_id=user_id, server_id=server_id)
#     taskId = len(tasks) + 1
#     # エンティティを追加する
#     entity = {
#         "PartitionKey": f"tasks-{user_id}",
#         "RowKey": f"{taskId}-{server_id}",
#         "TaskId": f"{taskId}",
#         "ServerId": f"{server_id}",
#         "TaskTitle": task_title,
#         "TaskDetail": task_detail,
#         "TaskStatus": task_status,
#         "TaskColor": task_color,
#     }

#     table_client = table_service_client.get_table_client(table_name)
#     table_client.upsert_entity(entity)
#     print("Entity added successfully.")

#     # エンティティを取得する
#     # retrieved_entity = table_client.get_entity(
#     #     partition_key=f"tasks-{user_id}", row_key=f"{taskId}"
#     # )
#     filter = f"PartitionKey eq 'tasks-{user_id}' and RowKey eq '{taskId}-{server_id}' and ServerId eq '{server_id}'"
#     entities = list(table_client.query_entities(query_filter=filter))
#     print("Retrieved Entity:")
#     print(entities)

#     return entities[0]


# async def update_tasks(user_id, server_id, task_id, task_status):
#     # テーブル名の指定
#     table_name = "tasks"

#     # テーブルクライアントの生成
#     table_client = table_service_client.get_table_client(table_name)

#     # エンティティの取得
#     try:
#         entity = table_client.get_entity(
#             partition_key=f"tasks-{user_id}", row_key=f"{task_id}-{server_id}"
#         )
#     except ResourceNotFoundError:
#         print(f"Task '{task_id}' not found.")
#         return

#     # ステータスの更新
#     entity["TaskStatus"] = task_status

#     # エンティティの更新
#     table_client.update_entity(entity, mode=UpdateMode.REPLACE)

#     print(f"Task '{task_id}' updated successfully.")

#     # 更新されたエンティティの取得
#     updated_entity = table_client.get_entity(
#         partition_key=f"tasks-{user_id}", row_key=f"{task_id}-{server_id}"
#     )

#     return updated_entity


# async def delete_tasks(user_id, server_id, task_id):
#     # テーブル名の指定
#     table_name = "tasks"

#     # テーブルクライアントの生成
#     table_client = table_service_client.get_table_client(table_name)

#     try:
#         delete_task = table_client.get_entity(
#             partition_key=f"tasks-{user_id}", row_key=f"{task_id}-{server_id}"
#         )
#     except ResourceNotFoundError:
#         print(f"Task '{task_id}' not found.")
#         return

#     # エンティティの削除
#     table_client.delete_entity(
#         partition_key=f"tasks-{user_id}", row_key=f"{task_id}-{server_id}"
#     )

#     print(f"Task '{task_id}' deleted successfully.")

#     return delete_task

