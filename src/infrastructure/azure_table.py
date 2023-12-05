# infrastructure/azure_table.py
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import os

class AzureTable:
    def __init__(self):
        # Azure Table Storage の接続文字列
        connection_string = os.environ["CONNECTION_STRING"]

        # テーブルサービスクライアントの作成
        self.table_service_client = TableServiceClient.from_connection_string(connection_string)
        self.table_name = "tasks"

        # テーブルの存在確認と作成
        try:
            self.table_service_client.create_table(self.table_name)
            print(f"Table '{self.table_name}' created successfully.")
        except ResourceExistsError:
            print(f"Table '{self.table_name}' already exists.")
    
    def get_tasks(self, user_id, server_id):
        table_client = self.table_service_client.get_table_client(self.table_name)
        filter = f"PartitionKey eq 'tasks-{user_id}' and ServerId eq '{server_id}'"
        entities = list(table_client.query_entities(query_filter=filter))
        return entities

    def create_task(self, task):
        table_client = self.table_service_client.get_table_client(self.table_name)
        entity = {
            "PartitionKey": f"tasks-{task.user_id}",
            "RowKey": f"{task.task_id}-{task.server_id}",
            "TaskId": f"{task.task_id}",
            "ServerId": f"{task.server_id}",
            "TaskTitle": task.task_title,
            "TaskDetail": task.task_detail,
            "TaskStatus": task.task_status,
            "TaskColor": task.task_color,
        }
        table_client.upsert_entity(entity)

    def update_task(self, task):
        table_client = self.table_service_client.get_table_client(self.table_name)
        entity = table_client.get_entity(
            partition_key=f"tasks-{task.user_id}", row_key=f"{task.task_id}-{task.server_id}"
        )
        entity["TaskStatus"] = task.task_status
        table_client.update_entity(entity, mode=UpdateMode.REPLACE)

    def delete_task(self, task):
        table_client = self.table_service_client.get_table_client(self.table_name)
        table_client.delete_entity(
            partition_key=f"tasks-{task.user_id}", row_key=f"{task.task_id}-{task.server_id}"
        )
