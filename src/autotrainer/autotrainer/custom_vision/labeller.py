
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import Project, Tag

class Labeller:

    tag_dictionary = {}
    def add_label_if_not_exists(self, trainer: CustomVisionTrainingClient, project: Project, tag_name: str)->Tag:
        """
        Adds a tag to the cache

        :param trainer: The project trainer
        :type: azure.cognitiveservices.vision.customvision.training.CustomVisionTrainingClient
        :param project: the Custom Vision project
        :type: string
        :param tag_name: the name of the tag to add
        :type: azure.cognitiveservices.vision.customvision.training.models.Project
        :returns: string
        """
        if len(self.tag_dictionary) == 0:
            tags=trainer.get_tags(project.id)
            for tag in tags:
                self.tag_dictionary[tag.name] = tag

        if tag_name not in self.tag_dictionary:
            self.tag_dictionary[tag_name] = trainer.create_tag(project.id, tag_name)

        return self.tag_dictionary[tag_name]