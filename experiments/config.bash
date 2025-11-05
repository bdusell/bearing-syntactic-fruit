# SINGULARITY_IMAGE_FILE should be the path of the .sif file to be used as the
# image for the Singularity container.
SINGULARITY_IMAGE_FILE=bearing-syntactic-fruit.sif
# BASE_DIR is a directory where all datasets, models, figures, etc. will be
# stored.
BASE_DIR=results
# SINGULARITY_ARGS contains extra arguments that will be passed to Singularity.
# You might need to add --bind arguments to give Singularity access to
# additional directories.
SINGULARITY_ARGS=()
