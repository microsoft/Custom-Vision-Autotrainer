# Custom-Vision-Autotrainer
An autotraining tool for customvision.ai using Azure Blob Storage and Azure Pipelines

[![Build Status](https://dev.azure.com/aussiedevcrew/Custom-Vision-Autotrainer/_apis/build/status/xtellurian.Custom-Vision-Autotrainer?branchName=master)](https://dev.azure.com/aussiedevcrew/Custom-Vision-Autotrainer/_build/latest?definitionId=6&branchName=master)

## Features

 * Data Catalogue
 * Train, Test, and Holdout sets
 * CLI, Python and CI/CD friendly
 * Get started quickly with local uploads
 * Store labels with images
 * Select data for training Custom Vision models
 * Train and export your models

### Data Catalogue

Backed by [Azure Storage](https://azure.microsoft.com/en-au/services/storage/), Autotrainer helps you maintain a large collection of labelled images for machine learning.

### Train, Test, and Holdout sets

Machine learning often requires the use of multiple datasets that must remain segregated. Autotrainer provides three containers for image datasets: train, test, and holdout.

 * Train: Used to training the model.
 * Test:  Used to test the model during training, and potentially join the training set.
 * Holdout: Validate your model using this unseen data.

### CLI, Python and CI/CD Friendly

Consume autotrainer via the CLI, in Python code, or run in [Azure Pipelines](https://azure.microsoft.com/en-au/services/devops/pipelines/).

### Get started quickly

Upload a set of images from a directory in a single command.

### Store labels with images

Labels are stored in special *label* files, right next to the image in blob storage.

### Select data for a Custom Vision project

Select images from your training set, and push them to a Custom Vision project.

### Train and export your models

Automate the training and exporting of models.

# Quickstart

## Docker

```sh
docker run -it -e "CV_ENDPOINT=https://southcentralus.api.cognitive.microsoft.com" -e "CV_TRAINING_KEY=your_key" -e "STORAGE_ACCOUNT_CONNECTION_STRING=your_connection_string" flanagan89/custom-vision-autotrainer -h
```

## Configuration

Autotrainer requires three environment variables:

 * `CV_ENDPOINT` : The location of your custom vision service, e.g. https://southcentralus.api.cognitive.microsoft.com
 * `CV_TRAINING_KEY` : Your custom vision training key
 * `STORAGE_ACCOUNT_CONNECTION_STRING` : Connection string to an Azure Storage Account

# Build

## Setup environment and install dependencies

I recommend using [Mini Conda](https://conda.io/en/latest/miniconda.html) to manage your python environment. Download and install miniconda, then in a shell:

1. Create a conda environment: `conda create -n customvisionautotrainer python=3.6`
2. Activate the environment: `activate customvisionautotrainer`. 
3. Install runtime dependencies: `pip install -r src/autotrainer/requirements.txt`
4. Install developer dependencies: `pip install -r src/autotrainer/requirements-dev.txt`
5. Configure environment variables (see above) 

## Run the Autotrainer CLI

```sh
$ cd src/autotrainer
$ python ./autotrainer_cli.py -h
usage: autotrainer [cv, catalogue, select] <options>

Autotrainer tools

positional arguments:
  command     Subcommand to run

optional arguments:
  -h, --help  show this help message and exit

$ python ./autotrainer_cli.py catalogue -h
usage: autotrainer catalogue <options>

Data Catalogue tools

positional arguments:
  {describe,upload}  Catalogue options

optional arguments:
  -h, --help         show this help message and exit
```

# Test

Autotrainer uses [nose](https://nose.readthedocs.io/en/latest/)

First, run Azurite for local blob storage testing:

```sh
$ cd src/
$ docker-compose up -d
```

Then you can run the tests.

```sh
$ cd src/autotrainer
$ nosetests
............
----------------------------------------------------------------------
Ran 12 tests in 7.088s

OK
``` 

> NOTE: Some tests require access to a *real* Azure Storage account and Custom Vision service. See the environment variable section above.


# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
