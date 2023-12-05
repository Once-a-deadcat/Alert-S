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
    
    def get_tasks_for_status(self, user_id):
        table_client = self.table_service_client.get_table_client(self.table_name)
        filter = f"PartitionKey eq 'tasks-{user_id}'"
        entities = list(table_client.query_entities(query_filter=filter))
        return entities
    
    def get_task(self, user_id, server_id, task_id):
        table_client = self.table_service_client.get_table_client(self.table_name)
        entity = table_client.get_entity(
            partition_key=f"tasks-{user_id}", row_key=f"{task_id}-{server_id}"
        )
        return entity

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
        return entity

    def update_task(self, user_id, server_id, task_id, task_status):
        table_client = self.table_service_client.get_table_client(self.table_name)
        taskEntity = self.get_task(user_id, server_id, task_id)
        taskEntity["TaskStatus"] = task_status
        table_client.update_entity(taskEntity, mode=UpdateMode.REPLACE)
        return taskEntity

    def delete_task(self, user_id, server_id, task_id):
        table_client = self.table_service_client.get_table_client(self.table_name)
        # 削除するエンティティを取得する
        entity = table_client.get_entity(
            partition_key=f"tasks-{user_id}", row_key=f"{task_id}-{server_id}"
        )
        table_client.delete_entity(
            partition_key=f"tasks-{user_id}", row_key=f"{task_id}-{server_id}"
        )
        return entity
