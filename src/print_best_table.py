import numpy

from print_table_util import (
    run_main,
    Column,
    format_text,
    format_float,
    format_mean_and_variance
)
from print_mean_table import read_txt, read_json_attr

def get_best_index(cache):
    trials = cache['trials']
    if trials:
        return numpy.argmin([
            trial.info['train']['best_validation_scores']['cross_entropy_per_token']
            for trial in trials
        ])

def get_best_trial(cache):
    trials = cache['trials']
    if trials:
        return trials[cache['best_index']]

def get_validation_cross_entropy(cache):
    best_trial = cache['best_trial']
    if best_trial:
        return best_trial.info['train']['best_validation_scores']['cross_entropy_per_token']

def get_test_conditional_probability(cache):
    return read_conditional_probability(cache, 'test-target')

def get_generalization_conditional_probability(cache):
    return read_conditional_probability(cache, 'generalization-target')

def get_generalization_conditional_cross_entropy(cache):
    return read_conditional_cross_entropy(cache, 'generalization-target')

def get_generalization_fine_accuracy(cache):
    return read_fine_accuracy(cache, 'generalization')

def get_generalization_log_ratio(cache):
    best_trial = cache['best_trial']
    if best_trial:
        return read_txt(best_trial, 'probability', 'generalization-ratio')

def read_conditional_probability(cache, dataset):
    best_trial = cache['best_trial']
    if best_trial:
        return read_json_attr(best_trial, 'probability', dataset, 'mean_sequence_probability')

def read_conditional_cross_entropy(cache, dataset):
    best_trial = cache['best_trial']
    if best_trial:
        return read_json_attr(best_trial, 'probability', dataset, 'cross_entropy_per_token')

def read_fine_accuracy(cache, dataset):
    best_trial = cache['best_trial']
    if best_trial:
        return read_txt(best_trial, 'fine-accuracy', dataset)

def main():
    col_format = format_float(places=3)
    run_main(
        header=r'''
& \multicolumn{1}{c}{Val.} & \multicolumn{1}{c}{Test} & \multicolumn{3}{c}{Generalization} \\
\cmidrule(lr){2-2} \cmidrule(lr){3-3} \cmidrule(lr){4-6}
'''.strip(),
        columns=[
            Column('Architecture', 'l', 'label', format_text()),
            Column('CE', 'S', 'validation_cross_entropy', col_format, bold_min=True),
            Column('CP $\\uparrow$', 'S', 'test_conditional_probability', col_format, bold_max=True),
            Column('CP $\\uparrow$', 'S', 'generalization_conditional_probability', col_format, bold_max=True),
            Column('CCE $\\downarrow$', 'S', 'generalization_conditional_cross_entropy', col_format, bold_min=True),
            Column('FA $\\uparrow$', 'S', 'generalization_fine_accuracy', col_format, bold_max=True),
            Column('Log Ratio $\\uparrow$', 'S', 'generalization_log_ratio', col_format, bold_max=True)
        ],
        callbacks={
            'best_index' : get_best_index,
            'best_trial' : get_best_trial,
            'validation_cross_entropy' : get_validation_cross_entropy,
            'test_conditional_probability' : get_test_conditional_probability,
            'generalization_conditional_probability' : get_generalization_conditional_probability,
            'generalization_conditional_cross_entropy' : get_generalization_conditional_cross_entropy,
            'generalization_fine_accuracy' : get_generalization_fine_accuracy,
            'generalization_log_ratio' : get_generalization_log_ratio
        }
    )

if __name__ == '__main__':
    main()
