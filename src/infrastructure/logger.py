import time
import logging
from io import StringIO
from typing import Callable
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import datetime

class AzureBlobHandler(logging.Handler):

    def __init__(self, connection_string, container_name, blob_name_prefix):
        super().__init__()
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_name_prefix = blob_name_prefix

    def emit(self, record):
        try:
            msg = self.format(record)
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            container_client = blob_service_client.get_container_client(self.container_name)
            timestamp = datetime.datetime.utcnow()
            folder_structure = timestamp.strftime("%Y/%m/%d")  # YYYY/MM/DD 形式
            filename = timestamp.strftime("%Y-%m-%d")  # YYYY-MM-DD 形式
            blob_name = f"{self.blob_name_prefix}/{folder_structure}/{filename}.log"
            blob_client = container_client.get_blob_client(blob_name)
            # Retrieve existing log data from the blob
            existing_data = ""
            if blob_client.exists():
                existing_data_stream = blob_client.download_blob()
                existing_data = existing_data_stream.content_as_text() + "\n"
            # Append the new log message to the existing data
            buffer = StringIO()
            buffer.write(existing_data)
            buffer.write(msg)
            buffer.seek(0)
            blob_client.upload_blob(buffer.getvalue(), overwrite=True)
        except Exception:
            self.handleError(record)
            