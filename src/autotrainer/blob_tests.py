import os
import uuid
import unittest
import requests
from azure.storage.blob import BlockBlobService
from autotrainer.blob.blob_client import BlobClient
from autotrainer.blob.models.container import Container

conn_string='DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1;'
block_blob_service = BlockBlobService(connection_string=conn_string)
test_file_name = 'dog1.jpg'
test_file = os.path.join( os.path.dirname(os.path.abspath(__file__)), ".." , "..", "sample_images", "dog", test_file_name)
print(test_file)

class InitBlobTests(unittest.TestCase):

    def tearDown(self):
        containers = block_blob_service.list_containers()
        for c in containers.items:
            print('deleting container ' + c.name)
            # block_blob_service.delete_container(c.name)

    def test_initialise_containers(self):
        blob_client=BlobClient(block_blob_service)
        blob_client.initialise_containers()

        containers = block_blob_service.list_containers()
        for n in Container:
            self.assertIn(n.name, [ c.name for c in containers.items])

class BlobTests(unittest.TestCase):

    parent_prefix= str(uuid.uuid4())
    test_container=str(uuid.uuid4()) + '-test'

    def setUp(self):
        block_blob_service.create_container(self.test_container)
    
    def tearDown(self):
        block_blob_service.delete_container(self.test_container)
    
    def test_add_training_from_path(self):
        blob_client=BlobClient(block_blob_service)
        parent =  self.parent_prefix + '1'
        blob_client.add_data_from_path(self.test_container, test_file, ['dog'], parent)

        blobs = block_blob_service.list_blobs(self.test_container)
        print([c.name for c in blobs.items])
        self.assertIn(parent + '/dog1.jpg', [c.name for c in blobs.items])
        self.assertIn(parent + '/dog1.jpg.labels', [c.name for c in blobs.items])

    def test_get_labelled_blob(self):
        blob_client=BlobClient(block_blob_service)
        parent = self.parent_prefix + '2' 
        labels = ['dog', 'cat']
        blob_client.add_data_from_path(self.test_container, test_file, labels, parent)
        labelled_blob = blob_client.get_labelled_blob_from_parent(self.test_container, parent, test_file_name)
        self.assertEqual(labelled_blob.labels, labels)

    def test_list_blob_names(self):
        blob_client=BlobClient(block_blob_service)
        parenta = self.parent_prefix + '3a' 
        parentb = self.parent_prefix + '3b' 
        labels = ['dog', 'cat']
        blob_client.add_data_from_path(self.test_container, test_file, labels, parenta )
        blob_client.add_data_from_path(self.test_container, test_file, labels, parentb )
        blob_names = blob_client.list_blob_names(self.test_container)
        self.assertIn(parenta + '/' + test_file_name, blob_names)
        self.assertIn(parentb + '/' + test_file_name, blob_names)
        parent_a_blobs = blob_client.list_blob_names(self.test_container, parenta)
        self.assertIn(parenta + '/' + test_file_name, parent_a_blobs)
        self.assertNotIn(parentb + '/' + test_file_name, parent_a_blobs)

    def test_download_url(self):
        blob_client=BlobClient(block_blob_service)
        parent = self.parent_prefix + '4' 
        labels = ['dog']
        blob_client.add_data_from_path(self.test_container, test_file, labels, parent)
        labelled_blob = blob_client.get_labelled_blob_from_parent(self.test_container, parent, test_file_name)

        response = requests.get(labelled_blob.download_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        self.assertTrue(len(response.content) > 0)
        with open(test_file, mode='rb') as file: # b is important -> binary
            fileContent = file.read()
            self.assertEqual(fileContent, response.content)

    def test_list_all_labelled_blobs(self):
        blob_client=BlobClient(block_blob_service)
        parent = self.parent_prefix + '5' 
        dog_label = ['dog']
        cat_label = ['cat']
        dogs_and_cats_label = ['dog','cat']
        blob_client.add_data_from_path(self.test_container, test_file, dog_label, parent + 'dog' )
        blob_client.add_data_from_path(self.test_container, test_file, cat_label, parent + 'cat' )
        blob_client.add_data_from_path(self.test_container, test_file, dogs_and_cats_label, parent + 'dogandcat')

        all_labelled_blobs = blob_client.list_all_labelled_blobs(self.test_container, None)
        all_labels = [s.labels for s in all_labelled_blobs]
        self.assertIn(dog_label, all_labels)
        self.assertIn(cat_label, all_labels)
        self.assertIn(dogs_and_cats_label, all_labels)
