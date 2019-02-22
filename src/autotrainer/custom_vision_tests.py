
import os
import unittest
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import Project, ImageUrlCreateEntry

from autotrainer.blob.blob_client import LabelledBlob

from autotrainer.custom_vision.custom_vision_client import CustomVisionClient
from autotrainer.custom_vision.domain import Domain, to_domain_id
from autotrainer.custom_vision.classification_type import ClassificationType

CVTK=os.environ['CV_TRAINING_KEY']
endpoint=os.environ['CV_ENDPOINT']
training_client = CustomVisionTrainingClient(CVTK, endpoint)

class CustomVisionTests(unittest.TestCase):
    projects: [Project]
    
    def tearDown(self):
        for project in self.projects:
            training_client.delete_project(project.id)
            self.projects.remove(project)

    def setUp(self):
        self.projects = []

    def test_create_project(self):
        client = CustomVisionClient(training_client)
        project = client.create_project('test', 'test', Domain.GENERAL_CLASSIFICATION, ClassificationType.MULTICLASS)
        self.projects.append(project) # add to delete later
        self.assertIsNotNone(project)
        self.assertIsInstance(project, Project)
        self.assertIn('test', project.name)
        projects = training_client.get_projects()
        self.assertIn(project, projects)

    def test_create_project_compact_multilabel(self):
        client = CustomVisionClient(training_client)
        project = client.create_project('test', 'test', Domain.GENERAL_CLASSIFICATION_COMPACT, ClassificationType.MULTILABEL)
        self.projects.append(project)
        self.assertIsNotNone(project)
        self.assertIsInstance(project, Project)
        self.assertIn('test', project.name)
        self.assertEqual(project.settings.domain_id, to_domain_id(Domain.GENERAL_CLASSIFICATION_COMPACT) )
        self.assertEqual(project.settings.classification_type, ClassificationType.MULTILABEL.value )
        
        projects = training_client.get_projects()
        self.assertIn(project, projects)

    def test_create_image_url_list(self):
        client = CustomVisionClient(training_client)
        project = client.create_project('test','test', Domain.GENERAL_CLASSIFICATION, ClassificationType.MULTICLASS)
        self.projects.append(project) # add to delete later
        labelled_blobs = [LabelledBlob('url1', ['tomato','potato']), LabelledBlob('url2', ['banana','fig'])]
        image_urls = client.create_image_url_list(project, labelled_blobs )
        for labelled_blob in labelled_blobs:
            self.assertIn(labelled_blob.download_url, [i.url for i in image_urls])
        for image in image_urls:
            self.assertIsInstance(image, ImageUrlCreateEntry)