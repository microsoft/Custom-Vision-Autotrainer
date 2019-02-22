import os
import uuid
from datetime import datetime, timedelta
from azure.storage.blob import ( 
    BlockBlobService,
    BlobPermissions
)
from azure.storage.blob.models import Blob
from autotrainer.blob.models.labelled_blob import LabelledBlob
from autotrainer.blob.models.container import Container

# Helper methods
def join_parent_and_file_name(parent:str, file_name: str)-> str:
    if parent:
        if not parent.endswith('/'):
            parent = parent + '/'
        return parent + file_name
    else:
        return file_name

def join_blob_name_for_labels(blob_name: str) -> str:
    return blob_name + '.labels'

def join_parent_and_file_name_labels(parent:str, file_name: str)-> str:
    if parent:
        if not parent.endswith('/'):
            parent = parent + '/'
        return join_blob_name_for_labels(parent + file_name)
    else:
        return join_blob_name_for_labels(file_name)
    
# main blob client class

class BlobClient:
    blob_service: BlockBlobService

    def __init__(self, blob_service: BlockBlobService):
        """
        :param block_blob_service: A block blob service
        :type: azure.storage.blob.BlockBlobService
        """
        self.blob_service = blob_service

    def initialise_containers(self):
        """
        Creates the containers required in the storage account
        """
        for c in Container:
            print('creating ' + c.value)
            self.blob_service.create_container(c.value)

    def add_data_from_path(self, container_name: str, file_path: str, labels: [str] = [], parent: str = None)->LabelledBlob:
        """
        Creates a new file in blob storage
        :param container_name: One of self.container_names
        :type: str
        :param file_path: Path to the file to upload
        :type: str
        :param parent: Directory in blob storage. None will create a new directory
        :type: str
        :param labels: List of labels for the file
        :type: [str]
        """
        filename=os.path.basename(file_path)
        blob_name = join_parent_and_file_name(parent, filename)
        labels_full_name = join_parent_and_file_name_labels(parent, filename)
        self.blob_service.create_blob_from_path(container_name, blob_name, file_path )
        text=''
        for label in labels:
            text+=label + '\n'
        
        self.blob_service.create_blob_from_text(container_name, labels_full_name, text.strip())
        return self.get_labelled_blob(container_name, blob_name)

    def list_blob_names(self, container_name: str, parent: str = None) -> [str]:
        return self.blob_service.list_blob_names(container_name, parent).items

    def get_labelled_blob_from_parent(self, container_name: str, parent: str, file_name: str, expiry_hours: int = 1)-> LabelledBlob :
        """
        Returns an object with a download url and labels array
        :param container_name: One of the container_names
        :type: str
        :param file_name: Name of the file
        :type: str
        :param parent: Directory in blob storage.
        :type: str
        :param expiry_hours: How long the SAS token will last for
        :type: int
        """
        blob_name = join_parent_and_file_name(parent, file_name)
        return self.get_labelled_blob(container_name, blob_name, expiry_hours)

    def get_labelled_blob(self, container_name: str, blob_name: str, expiry_hours: int = 1)->LabelledBlob:
        labels_blob_name = join_blob_name_for_labels(blob_name)
        labels = []
        if(self.blob_service.exists(container_name, labels_blob_name)):
            labels_blob = self.blob_service.get_blob_to_text(container_name, labels_blob_name)
            if labels_blob:
                labels = labels_blob.content.split('\n')

        sas = self.blob_service.generate_blob_shared_access_signature( 
            container_name, blob_name, 
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours))

        url = self.blob_service.make_blob_url(container_name, blob_name, sas_token=sas)
        res = LabelledBlob(url, labels)
        return res

    def to_labelled_blob(self, container_name:str, blob: Blob ):
        if blob.name.endswith('.labels'):
            raise ValueError('Cannot convert a .labels file to a LabelledBlob')
        return self.get_labelled_blob(container_name, blob.name)


    def list_all_labelled_blobs(self, container_name: str, num_results: int = None, expiry_hours:int = 1) -> [LabelledBlob]:
        """
        Returns an list of LabelledBlobs, each with a download url and labels array
        :param container_name: One of the container_names
        :type: str
        :param num_results: How many to return. 
        :type: int
        :param expiry_hours: How long the SAS token will last for
        :type: int
        """
        if(num_results == None):
            blobs = self.blob_service.list_blobs(container_name)
        else:
            blobs = self.blob_service.list_blobs(container_name, num_results= num_results * 2) # don't bother getting more than double the max
        blobs = [blob for blob in blobs if not blob.name.endswith('.labels')] # remove labels
        res = []
        for blob in blobs:
            res.append(self.to_labelled_blob(container_name, blob))
        return res

# factory methods
def create_blob_client(account_name:str, key: str)-> BlobClient:
    blockblocksvc = BlockBlobService(account_name, key)
    return BlobClient(blockblocksvc)

def create_blob_client_from_connection_string(conn_string: str):
    blockblocksvc = BlockBlobService(connection_string=conn_string)
    return BlobClient(blockblocksvc)
