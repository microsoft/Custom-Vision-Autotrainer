import time
import msrest
from autotrainer.custom_vision.platform import Platform, Flavour
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import Iteration, Project, Export

class Exporter:
    training_client: CustomVisionTrainingClient

    def __init__(self, training_client: CustomVisionTrainingClient):
        self.training_client = training_client

    def export(self, platform: Platform, flavour: Flavour, project: Project, iteration: Iteration = None)-> Export:

        exports=self.training_client.get_exports(project.id, iteration.id)
        print('there are {} existing exports'.format(len(exports)))

        try:
            exported=self.training_client.export_iteration(project.id, iteration.id, platform.value, flavour.value)
            while (exported.status != 'Done'):
                if(exported.status == 'Failed'):
                    print('export failed for iteration {}'.format(iteration.id))
                    break
                else:
                    exports = self.training_client.get_exports(project.id, iteration.id)
                    exported=next(ex for ex in exports if ex.platform == platform.value)
                    print ("Exporting status: " + exported.status)
                    time.sleep(1)
        except msrest.exceptions.HttpOperationError as err:
            print(err.message)
            print(err.inner_exception)
            print('iteration {} failed to export. Using older export'.format(iteration.id))
            exported=exports[0]
        return exported

