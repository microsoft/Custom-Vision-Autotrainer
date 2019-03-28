import os
import unittest
import uuid
from urllib.parse import urlparse
from autotrainer.table.table_client import (
    TableClient,
    create_table_client_from_connection_string)
from azure.cognitiveservices.vision.customvision.training.models import (
    ImageCreateResult,
    Image)

conn_string = os.environ['STORAGE_ACCOUNT_CONNECTION_STRING']
test_container = "test_container"
table_name = "test"


class TableTests(unittest.TestCase):

    table: TableClient
    test_record: ImageCreateResult

    def setUp(self):
        self.table = create_table_client_from_connection_string(conn_string)
        self.table.initialise_table(table_name=table_name)
        test = ImageCreateResult()
        test_image = Image()
        test_image.id = str(uuid.uuid4())
        test.image = test_image
        test.source_url = "https://test.com/1.jpg"
        self.test_record = test
        pass

    def tearDown(self):
        pass

    def insert_record(self):
        test = self.test_record

        url = urlparse(test.source_url)

        self.table.insert_record(test, test_container)
        record = self.table.get_record(test_container, test.image.id)

        self.assertEqual(test.image.id, record.RowKey)
        self.assertEqual(url.netloc + url.path, record.url)

    def test_delete_record(self):
        test = self.test_record
        fileName = urlparse(test.source_url).path.split("/")[-1]
        self.table.insert_record(test, test_container)
        self.table.delete_record(test_container, fileName)
        try:
            record = self.table.get_record(test_container, fileName)
        except Exception as e:
            self.assertIsNotNone(e)
            return
        self.assertIsNone(record)

    def test_delete_table(self):
        self.table.delete_table()
        self.assertFalse(self.table.table_service.exists(table_name))
