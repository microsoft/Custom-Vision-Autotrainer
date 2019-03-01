from azure.cosmosdb.table.tableservice import TableService
from urllib.parse import urlparse


# main table client class
class TableClient:
    blob_service: TableService

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

    def insert_record(self, item):
        url = urlparse(item.download_url)
        keys = url.path.split("/")
        record = {'PartitionKey': keys[1], 'RowKey': keys[2]}
        self.table_service.insert_entity(self.table_name, record)


def create_table_client(account_name: str, key: str) -> TableClient:
    tablesvc = TableService(account_name, key)
    return TableClient(tablesvc)


def create_table_client_from_connection_string(conn_string: str):
    tablesvc = TableService(connection_string=conn_string)
    return TableClient(tablesvc)
