import os
import unittest
import uuid
from azure.cognitiveservices.vision.customvision.training.models import Project
from azure.cognitiveservices.vision.customvision.training.models import (
    ImageCreateResult,
    Image)
from autotrainer.blob.models.container import Container
from autotrainer.autotrainer import Autotrainer
from autotrainer.custom_vision.domain import Domain
from autotrainer.custom_vision.classification_type import ClassificationType

conn_string = os.environ['STORAGE_ACCOUNT_CONNECTION_STRING']
CVTK = os.environ['CV_TRAINING_KEY']
cv_endpoint = os.environ['CV_ENDPOINT']

dog_dir = "../../sample_images/dog"
cat_dir = "../../sample_images/cat"
test_container = "test_container"


class AutotrainerTests(unittest.TestCase):
    autotrainer: Autotrainer
    projects: [Project]

    def setUp(self):
        self.autotrainer = Autotrainer(CVTK, cv_endpoint, conn_string)
        self.autotrainer.blob.initialise_containers()
        self.projects = []

    def tearDown(self):
        for project in self.projects:
            print('deleting project id {}'.format(project.id))
            self.autotrainer.custom_vision.training_client.delete_project(
                project.id)
            self.projects.remove(project)

    def test_upload_files(self):
        image_paths = self.autotrainer.get_file_paths(dog_dir, 'jpg')

        self.autotrainer.upload_multiple_images(
            Container.test,
            image_paths,
            ['dog'])

    def test_add_images_to_project(self):
        project = self.autotrainer.custom_vision.create_project(
            'test_add_images',
            'created by unit test',
            Domain.GENERAL_CLASSIFICATION,
            ClassificationType.MULTICLASS)

        self.projects.append(project)  # save to delete later
        image_paths = self.autotrainer.get_file_paths(cat_dir, 'jpg')

        self.autotrainer.upload_multiple_images(
            Container.test,
            image_paths,
            ['cat'])

        self.autotrainer.add_all_images_to_cv(Container.test, project.id)

    def test_add_record(self):
        test_list = []
        test = ImageCreateResult()
        test_image = Image()
        test_image.id = str(uuid.uuid4())
        test.image = test_image
        test.source_url = "https://test.com/1.jpg"
        test_list.append(test)

        test.image.id = str(uuid.uuid4())
        test_list.append(test)

        self.autotrainer.table.initialise_table(table_name="testAutoTrainer")
        self.autotrainer.create_record_of_images(test_list, test_container)

        record = self.autotrainer.table.get_record(
            test_container,
            test.image.id)

        self.assertEqual(record.RowKey, test.image.id)
        self.assertEqual(record.PartitionKey, test_container)

        self.autotrainer.table.delete_table()
