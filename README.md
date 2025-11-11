# Bearing Syntactic Fruit with Stack-Augmented Neural Networks

This repository contains the code for the paper "Bearing Syntactic Fruit with
Stack-Augmented Neural Networks" (DuSell & Cotterell, 2025). It includes all of
the code necessary to reproduce the experiments and figures in the paper, as
well as a Docker image definition that can be used to replicate the software
environment it was developed in.

## Directory Structure

* `experiments/`: High-level scripts for reproducing all of the experiments and
  figures in the paper using the code in `src/`.
* `scripts/`: Helper scripts for setting up the software environment, building
  container images, running containers, installing Python packages, etc.
  Instructions for using these scripts are below.
* `src/`: Source code for running all experiments.

The source code for all neural network architectures (including the
stack-augmented neural network architectures), training algorithms, and
evaluation algorithms are in a
[separate repository, which may be found here](https://github.com/bdusell/rau/tree/1b80c20314ed0a95402b24c1253ff25b87a161da).
Following the instructions below will install it automatically into a local
Python virtual environment using [Poetry](https://python-poetry.org/).

## Installation and Setup

In order to foster reproducibility, the code for this paper was developed and
run inside of a [Docker](https://www.docker.com/) container defined in the file
[`Dockerfile-dev`](Dockerfile-dev). To run this code, you can build the
Docker image yourself and run it using Docker. Or, if you don't feel like
installing Docker, you can simply use `Dockerfile-dev` as a reference for
setting up the software environment on your own system. You can also build
an equivalent [Singularity](https://sylabs.io/docs/#singularity) image which
can be used on an HPC cluster, where it is likely that Docker is not available
but Singularity is. There is a script that automatically sets up the Docker
container and opens a shell in it (instructions below).

### Using Docker

In order to use the Docker image, you must first
[install Docker](https://www.docker.com/get-started).
If you intend to run any experiments on a GPU, you must also ensure that your
NVIDIA driver is set up properly and install the
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

In order to automatically build the Docker image, start the container, and open
up a bash shell inside of it, run

    $ bash scripts/docker_shell.bash --build

After you have built the image once, there is no need to do so again, so
afterwards you can simply run

    $ bash scripts/docker_shell.bash

By default, this script starts the container in GPU mode, which will fail if
you are not running on a machine with a GPU. If you only want to run things in
CPU mode, you can run

    $ bash scripts/docker_shell.bash --cpu

### Using Singularity

Singularity is an alternative container runtime that is more suitable for
shared computing environments. Note: Singularity also goes by the name
Apptainer; they refer to the same thing.

In order to run the code in a Singularity container, you must first obtain the
Docker image and then convert it to a `.sif` (Singularity image) file on a
machine where you have root access (for example, your personal computer or
workstation). This requires installing both Docker and
[Singularity](https://docs.sylabs.io/guides/latest/user-guide/quick_start.html)
on that machine. Assuming you have already built the Docker image according to
the instructions above, you can use the following to create the `.sif` file:

    $ bash scripts/build_singularity_image.bash

This will create the file `bearing-syntactic-fruit.sif`. It is normal for this
to take several minutes. Afterwards, you can upload the `.sif` file to your HPC
cluster and use it there.

You can open a shell in the Singularity container using

    $ bash scripts/singularity_shell.bash

This will work on machines that do and do not have an NVIDIA GPU, although it
will output a warning if there is no GPU.

### Additional Setup

Whatever method you use to run the code (whether in a Docker container,
Singularity container, or no container), you must run this script once (*inside
the container shell*):

    $ bash scripts/install_python_packages.bash

This script installs the Python packages required by our code into a local
virtual environment using Poetry.

## Running Code

All files under `src/` should be run using Poetry so they have access to the
Python packages installed in Poetry's virtual environment. This means you should
either prefix all of your commands with `bash scripts/poetry_run.bash` or run
`bash scripts/poetry_shell.bash` beforehand to enter a shell with Poetry's
virtualenv enabled all the time. You should run both Python and Bash scripts
with Poetry, because the Bash scripts might call out to Python scripts. All Bash
scripts under `src/` should be run with `src/` as the current working directory.

All scripts under `scripts/` and `experiments/` should be run without Poetry
with the top-level directory as the current working directory.

## Running Experiments

The [`experiments/`](experiments) directory contains scripts for reproducing all
of the experiments and tables presented in the paper. Some of these scripts are
intended to be used to submit jobs to a computing cluster. All scripts should be
run outside of the container. You will need to edit the file
[`experiments/submit_job.bash`](experiments/submit_job.bash) to tailor it to
your specific computing cluster.

You should also edit the file
[`experiments/config.bash`](experiments/config.bash)
to configure `BASE_DIR` to be a directory where all data and experimental
results will be stored.

### Downloading and Preprocessing Datasets

The relevant scripts are under `experiments/preprocessing/`.

* `download_data.bash`: Download the datasets.
* `submit_prepare_data_jobs.bash`: Prepare the data to be loaded by the neural
  network training and evaluation code.

### Training Models

The relevant scripts are under `experiments/training/`. They should be run
after datasets are downloaded and prepared.

* `submit_hyperparameter_search_jobs.bash`: Train all models used for the
  initial hyperparameter search.
* `submit_continue_hyperparameter_search_jobs.bash`: In case the training of any
  of the above models is interrupted, this can be used to recover from crashes
  and restart training.
* `submit_train_and_evaluate_tuned_model_jobs.bash`: After all models used for
  the hyperparameter search have been trained, train and evaluate models using
  the best hyperparameter settings.
* `submit_continue_train_and_evaluate_tuned_model_jobs.bash`: In case the
  training of any of the above models is interrupted, this can be used to
  recover from crashes and restart training.

### Analysis

The relevant scripts are under `experiments/analysis/`. They should be run after
the models are trained and evaluated, although they report partial results
gracefully.

* `print_table.bash`: Print the main table of results for each task.
