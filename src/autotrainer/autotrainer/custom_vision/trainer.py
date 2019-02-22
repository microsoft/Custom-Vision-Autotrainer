import time
import msrest
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import Project, Iteration

class Trainer:
    training_client: CustomVisionTrainingClient

    def __init__(self, training_client: CustomVisionTrainingClient):
        self.training_client = training_client

    def train_and_wait(self, project: Project) -> Iteration:
        iterations=self.training_client.get_iterations(project.id)

        if(len(iterations) > 9):
            print('Max iterations (10) reached.')
            oldest_iteration=iterations[-1]
            if(oldest_iteration.is_default):
                second_oldest_iteration=iterations[-2]
                print('Deleting second oldest iteration - id: {}, name: {}'.format(second_oldest_iteration.id, second_oldest_iteration.name))
                self.training_client.delete_iteration(project.id, second_oldest_iteration.id)
            else:
                print('Deleting the oldest iteration - id: {}, name: {}'.format(oldest_iteration.id, oldest_iteration.name))
                self.training_client.delete_iteration(project.id, oldest_iteration.id)
        

        print ("Training...")
        try:
            iteration = self.training_client.train_project(project.id)
            while (iteration.status != "Completed"):
                if(iteration.status == "Failed"):
                    print('training failed for iteration {}'.format(iteration.id))
                    break
                else:
                    iteration = self.training_client.get_iteration(project.id, iteration.id)
                    print ("Training status: " + iteration.status)
                    time.sleep(1)
        except msrest.exceptions.HttpOperationError as err:
            print('Http error from Custom Vision: {}'.format(err.message))
            print('Failed to train model - perhaps nothing has changed.')
            iteration = iterations[0]
        
        return iteration
        