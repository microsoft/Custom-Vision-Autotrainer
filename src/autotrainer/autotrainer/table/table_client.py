from azure.cosmosdb.table.tableservice import TableService
from azure.cognitiveservices.vision.customvision.training.models import ImageCreateResult
from azure.cosmosdb.table.models import Entity
from urllib.parse import urlparse


# main table client class
class TableClient:
    table_service: TableService

    def __init__(self, table_service: TableService):
        """
        :param table_service: A table service
        :type: azure.cosmosdb.table.TableService
        """
        self.table_service = table_service
        self.table_name = "assets"
        self.initialise_table()

    def initialise_table(self):
        if self.table_service.exists(self.table_name) is False:
            self.table_service.create_table(self.table_name)

    def insert_record(self, item: ImageCreateResult, container_name: str):
        if item.image is not None:
            url = urlparse(item.source_url)
            record = {'PartitionKey': container_name, 'RowKey': item.image.id, 'url': url.netloc + url.path}
            self.table_service.insert_or_replace_entity(self.table_name, record)
        else:
            print("Skipping none image file.")

    def get_record(self, container_name: str, image_id: str) -> Entity:
        return self.table_service.get_entity(self.table_name, container_name, image_id)


def create_table_client(account_name: str, key: str) -> TableClient:
    tablesvc = TableService(account_name, key)
    return TableClient(tablesvc)


def create_table_client_from_connection_string(conn_string: str):
    tablesvc = TableService(connection_string=conn_string)
    return TableClient(tablesvc)
