import pathlib
import subprocess

from rau.tasks.common.training_loop import TrainingLoopState
from rau.tools.torch.saver import ModelSaver

def evaluate_overtrained(
    state: TrainingLoopState,
    saver: ModelSaver,
    index: int,
    base_dir: str,
    task_style: str,
    dataset_name: str,
    architecture: str,
    trial_no: str
) -> None:
    n = state.training_loop.every_n_examples[index][0]
    remainder = state.examples_since_every_n_examples[index]
    iteration_no = state.every_n_examples_no[index]
    num_examples = n * max(0, iteration_no - 1) + remainder
    model_dir = pathlib.Path(base_dir) / 'models' / 'overtrained-linear' / task_style / dataset_name / architecture / trial_no
    iteration_dir = model_dir / str(iteration_no)
    temp_model_dir = model_dir / 'temp'
    temp_saver = saver.to_directory(temp_model_dir)
    temp_saver.save_kwargs()
    temp_saver.save_parameters()
    subprocess.run([
        'bash',
        'evaluate_overtrained.bash',
        base_dir,
        task_style,
        dataset_name,
        str(temp_model_dir),
        str(iteration_dir),
        str(num_examples)
    ], check=True)
