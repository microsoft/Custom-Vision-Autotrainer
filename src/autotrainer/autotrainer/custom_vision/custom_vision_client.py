import math
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import Project, Iteration, ImageUrlCreateEntry, Tag, ImageCreateResult, Export

from autotrainer.custom_vision.domain import Domain, to_domain_id
from autotrainer.custom_vision.classification_type import ClassificationType
from autotrainer.custom_vision.labeller import Labeller
from autotrainer.custom_vision.trainer import Trainer
from autotrainer.custom_vision.balancer import Balancer
from autotrainer.custom_vision.exporter import Exporter
from autotrainer.custom_vision.platform import Platform, Flavour


from autotrainer.blob.blob_client import LabelledBlob

class CustomVisionClient:
    training_client: CustomVisionTrainingClient

    def __init__(self, training_client: CustomVisionTrainingClient):
        self.training_client = training_client

    def create_project(self, name: str, desc: str, domain: Domain, classification_type: ClassificationType)-> Project :
        domain_id = to_domain_id(domain)
        project = self.training_client.create_project(
            name, 
            description=desc, 
            domain_id= domain_id,
            classification_type=classification_type.value)
        return project

    def create_image_url_list(self, project: Project, labelled_blobs: [LabelledBlob])-> [ImageUrlCreateEntry]:
        labeller = Labeller()
        image_url_create_list = []
        for labelled_blob in labelled_blobs:
            tag_ids = []
            for label in labelled_blob.labels:
                tag_ids.append(labeller.add_label_if_not_exists(self.training_client, project, label).id)
            image_url_create_list.append( ImageUrlCreateEntry(url=labelled_blob.download_url, tag_ids=tag_ids ))
        return image_url_create_list

    def add_images_to_project(self, project: Project, image_url_create_entries: [ImageUrlCreateEntry])-> [ImageCreateResult]:

        batch = 64
        num_ops_required = math.ceil(len(image_url_create_entries) / batch) # just going to assume that 64 images won't have more than 20 tags
        images = []
        for x in range(num_ops_required):
            start = x * batch
            end = min(start + batch, len(image_url_create_entries)) # either the batch or the end of the list
            subset = image_url_create_entries[start:end]
            image_create_summary = self.training_client.create_images_from_urls(project.id, subset)
            print('Uploaded {} images from: {} to: {} of: {}'.format(len(subset), start, end, len(image_url_create_entries)))
            images.extend(image_create_summary.images)

        return images
    
    def balance_images(self, images: [ImageUrlCreateEntry]):
        balancer = Balancer(images)
        return balancer.apply()

    def train_project_and_wait(self, project: Project) -> Iteration:
        trainer = Trainer(self.training_client)
        return trainer.train_and_wait(project)

    def export_project(self, platform: Platform, flavour: Flavour, project: Project, iteration: Iteration )-> Export:
        if iteration.exportable:
            exporter = Exporter(self.training_client)
            return exporter.export(platform, flavour, project, iteration )

    def list_project_ids(self) -> [Project]:
        return self.training_client.get_projects()

# factory method
def create_cv_client(endpoint: str, key: str)-> CustomVisionClient:
    trainer = CustomVisionTrainingClient(key, endpoint)
    return CustomVisionClient(trainer)