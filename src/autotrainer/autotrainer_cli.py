import os
import argparse
import sys
import time
from collections import Counter

from autotrainer.autotrainer import Autotrainer
from autotrainer.custom_vision.domain import Domain
from autotrainer.custom_vision.classification_type import ClassificationType
from autotrainer.custom_vision.platform import Platform, Flavour
from autotrainer.blob.models.container import Container
from autotrainer.blob.models.labelled_blob import LabelledBlob

class AutotrainerCli:
    cv_key: str
    cv_endpoint: str
    storage_connection_string: str
    autotrainer: Autotrainer
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Autotrainer tools',
            usage='autotrainer [cv, catalogue, select] <options>')

        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        
        # setup the keys from environment variables
        self.cv_key = os.environ['CV_TRAINING_KEY']
        self.cv_endpoint=os.environ['CV_ENDPOINT']
        self.storage_connection_string=os.environ['STORAGE_ACCOUNT_CONNECTION_STRING']
        self.autotrainer = Autotrainer(self.cv_key, self.cv_endpoint, self.storage_connection_string)
        
        getattr(self, args.command)() # call the method on this obj

    def cv(self):
        
        parser = argparse.ArgumentParser(
            description='Custom Vision tools',
            usage= 'autotrainer cv <options>')
        # prefixing the argument with -- means it's optional
        parser.add_argument('--newproject', help='Name of the new project. Returns project id')
        parser.add_argument('--domain', type=Domain, choices=list(Domain), default=Domain.GENERAL_CLASSIFICATION)
        parser.add_argument('--type', type=ClassificationType, choices=list(ClassificationType), default=ClassificationType.MULTICLASS)
        parser.add_argument('--project', help='Id of the custom vision project')
        parser.add_argument('--train', help='Train a project. Returns iteration id', action='store_true')
        parser.add_argument('--export', help='Export a project', action='store_true')
        parser.add_argument('--iteration', help='(optional) iteration to store')
        parser.add_argument('--platform', help='Platform to export to', type=Platform, choices=list(Platform), default=Platform.DOCKER)
        parser.add_argument('--flavour', help='Platform dependent Flavour', type=Flavour, choices=list(Flavour), default=Flavour.Linux)
        parser.add_argument('--listprojects', help='list custom vision project IDs', action='store_true')
        args = parser.parse_args(sys.argv[2:])
        if(args.newproject):
            print('Creating new project: ' + args.newproject)
            project = self.autotrainer.custom_vision.create_project(args.newproject, 'Created by autotrainer CLI', args.domain, args.type )
            print(project.id)
        elif args.train:
            project = self.autotrainer.custom_vision.training_client.get_project(args.project)
            print('Training project: {}'.format(project.name))
            iteration = self.autotrainer.custom_vision.train_project_and_wait(project)
            print(iteration.id)
        elif args.export:
            project = self.autotrainer.custom_vision.training_client.get_project(args.project)
            if(args.iteration):
                iteration = self.autotrainer.custom_vision.training_client.get_iteration(project.id, args.iteration)
            else:
                iteration = self.autotrainer.custom_vision.training_client.get_iterations(project.id)[0]
            if not iteration.exportable:
                print('Iteration is not exportable')
                exit(1)
            export = self.autotrainer.custom_vision.export_project(args.platform, args.flavour, project, iteration)
            print(export.download_uri)
        elif args.listprojects:
            ids = self.autotrainer.custom_vision.list_project_ids()
            print("{:25s}{:}".format("Project Name", "Project ID"))
            print("-------------------------------------------------------------")
            for i in ids:
                print("{:25s}{:}".format(i.name, i.id))
        else:
            print('Incorrect syntax')

    def catalogue(self):
        # define the CLI args
        parser = argparse.ArgumentParser(
            description='Data Catalogue tools',
            usage='autotrainer catalogue <options>')
        parser.add_argument('command', help='Catalogue options',type=str, choices=['describe', 'upload'] )
        args = parser.parse_args(sys.argv[2:3])
        
        if args.command == 'describe':
            parser = argparse.ArgumentParser(
                description='Data Catalogue description',
                usage='autotrainer catalogue describe')
            print('Querying catalogue...')
            train_blobs = self.autotrainer.list_all_labelled_blobs(Container.train, None)
            test_blobs = self.autotrainer.list_all_labelled_blobs(Container.test, None)
            holdout_blobs = self.autotrainer.list_all_labelled_blobs(Container.holdout, None)
            print('Training set has {} images'.format(len(train_blobs)))
            print_describe_label_frequency(train_blobs)
            print('Test set has {} images'.format(len(test_blobs)))
            print_describe_label_frequency(test_blobs)
            print('Holdout set has {} images'.format(len(holdout_blobs)))
            print_describe_label_frequency(holdout_blobs)

        elif args.command == 'upload':
            parser = argparse.ArgumentParser(
                description='Upload to the data catalogue (blob storage)',
                usage='autotrainer catalogue upload <options>')
            parser.add_argument('-d', '--directory', help='The local directory containing the images', required=True)
            parser.add_argument('-l', '--labels', action='append', help='Label for the image', required=True) # can set multiple
            parser.add_argument('-c','--container', type=Container, choices=list(Container), default=Container.train)
            parser.add_argument('--extension', help='Filter on file extension', default='')
            parser.add_argument('--parent', help='Parent directory in Blob Storage', default=None)
            args = parser.parse_args(sys.argv[3:])
            image_paths = self.autotrainer.get_file_paths(args.directory, args.extension)
            labelled_blobs = self.autotrainer.upload_multiple_images(args.container, image_paths, args.labels, args.parent )
            print('Created {} labelled blobs'.format(len(labelled_blobs)))
        
    def select(self):
        # define the CLI args
        parser = argparse.ArgumentParser(
            description='Select data from blobs and add to Custom Vision',
            usage='autotrainer select <options>')
        parser.add_argument('-c','--container', type=Container, choices=list(Container), default=Container.train)
        parser.add_argument('--num', type=int, help='Number to add', required=False)
        parser.add_argument('--project', help='Id of the custom vision project', required=True)
        args = parser.parse_args(sys.argv[2:])

        res = self.autotrainer.add_all_images_to_cv(args.container, args.project, args.num )

        res_freq = Counter([i.status for i in res])
        print('{} image create results'.format(len(res)))
        print('label summary:')
        print(res_freq)


def print_describe_label_frequency(labelled_blobs: [LabelledBlob]):
    # print(set(labelled_blobs))
    seq = [i.labels for i in labelled_blobs]
    label_freq = Counter(x for xs in seq for x in set(xs))
    print(label_freq)

if __name__ == '__main__':
    AutotrainerCli()