from azure.cognitiveservices.vision.customvision.training.models import ImageCreateResult
from autotrainer.custom_vision.custom_vision_client import CustomVisionClient, create_cv_client
from autotrainer.table.table_client import TableClient, create_table_client_from_connection_string
from autotrainer.blob.blob_client import BlobClient, create_blob_client_from_connection_string
from autotrainer.blob.models.container import Container
from autotrainer.blob.models.labelled_blob import LabelledBlob
from autotrainer.local.file_loader import list_paths

class Autotrainer:

    custom_vision: CustomVisionClient
    blob: BlobClient
    def __init__(self, cv_key: str, cv_endpoint: str, storage_connection_string:str):
        self.custom_vision = create_cv_client(cv_endpoint, cv_key)
        self.blob = create_blob_client_from_connection_string(storage_connection_string)
        self.table = create_table_client_from_connection_string(storage_connection_string)

    def get_file_paths(self, directory_path: str, ext: str = '')->[str]:
        return list_paths(directory_path, ext)

    def list_all_labelled_blobs(self, container: Container, num_results: int = None):
        return self.blob.list_all_labelled_blobs(container.value, num_results)

    def upload_multiple_images(self, container: Container, image_paths: [str], labels: [str], parent: str = None)-> [LabelledBlob]:
        labelled_blobs = []
        for path in image_paths:
            labelled_blobs.append(self.blob.add_data_from_path(container.value, path, labels, parent ))

        for meta in labelled_blobs:
            self.table.insert_record(meta)

        return labelled_blobs

    def add_all_images_to_cv(self, container: Container, projectId: str, num_results: int = None)->[ImageCreateResult]:
        labelled_blobs = self.blob.list_all_labelled_blobs(container.value, num_results)
        project = self.custom_vision.training_client.get_project(projectId)
        images = self.custom_vision.create_image_url_list(project, labelled_blobs)
        images = self.custom_vision.balance_images(images)
        return self.custom_vision.add_images_to_project(project, images )
        # todo - save ids back to the blob storage
