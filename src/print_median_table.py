import math
import sys

import numpy

from print_table_util import (
    run_main,
    Column,
    format_text,
    format_float,
    format_mean_and_variance
)

def mean_and_std(values):
    if values:
        return numpy.median(values)

def get_validation_cross_entropy(cache):
    return mean_and_std([
        t.info['train']['best_validation_scores']['cross_entropy_per_token']
        for t in cache['trials']
    ])

def get_test_full_match_accuracy(cache):
    return read_full_match_accuracy(cache, 'test')

def get_generalization_full_match_accuracy(cache):
    return read_full_match_accuracy(cache, 'generalization')

def get_generalization_fine_accuracy(cache):
    return read_fine_accuracy(cache, 'generalization')

def get_test_cross_entropy(cache):
    return read_cross_entropy(cache, 'test')

def get_test_conditional_cross_entropy(cache):
    return read_cross_entropy(cache, 'test-target')

def get_generalization_cross_entropy(cache):
    return read_cross_entropy(cache, 'generalization')

def get_generalization_conditional_cross_entropy(cache):
    return read_cross_entropy(cache, 'generalization-target')

def read_txt(trial, subdir, dataset):
    file_path = trial.path / 'eval' / subdir / f'{dataset}.txt'
    try:
        text = file_path.read_text()
    except FileNotFoundError:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    return result

def read_full_match_accuracy_from_trial(trial, dataset):
    return read_txt(trial, 'greedy', dataset)

def read_full_match_accuracy(cache, dataset):
    return mean_and_std([
        read_full_match_accuracy_from_trial(t, dataset)
        for t in cache['trials']
    ])

def read_fine_accuracy_from_trial(trial, dataset):
    return read_txt(trial, 'fine-accuracy', dataset)

def read_fine_accuracy(cache, dataset):
    return mean_and_std([
        read_fine_accuracy_from_trial(t, dataset)
        for t in cache['trials']
    ])

def read_cross_entropy_from_trial(trial, dataset):
    return read_txt(trial, 'cross-entropy', dataset)

def read_cross_entropy(cache, dataset):
    return mean_and_std([
        read_cross_entropy_from_trial(t, dataset)
        for t in cache['trials']
    ])

def main():
    places = (3, 2)
    col_format = format_float(places=3)
    run_main(
        columns=[
            Column('Architecture', 'l', 'label', format_text()),
            Column('Val.\\ CE $\\downarrow$', 'c', 'validation_cross_entropy', col_format, bold_min=True),
            Column('Test Acc.\\ $\\uparrow$', 'c', 'test_full_match_accuracy', col_format, bold_max=True),
            Column('Test CE $\\downarrow$', 'c', 'test_cross_entropy', col_format, bold_min=True),
            Column('Test CCE $\\downarrow$', 'c', 'test_conditional_cross_entropy', col_format, bold_min=True),
            Column('Gen.\\ Acc.\\ $\\uparrow$', 'c', 'generalization_full_match_accuracy', col_format, bold_max=True),
            Column('Gen.\\ FA\\ $\\uparrow$', 'c', 'generalization_fine_accuracy', col_format, bold_max=True),
            Column('Gen.\\ CE $\\downarrow$', 'c', 'generalization_cross_entropy', col_format, bold_min=True),
            Column('Gen.\\ CCE $\\downarrow$', 'c', 'generalization_conditional_cross_entropy', col_format, bold_min=True)
        ],
        callbacks={
            'validation_cross_entropy' : get_validation_cross_entropy,
            'test_full_match_accuracy' : get_test_full_match_accuracy,
            'test_cross_entropy' : get_test_cross_entropy,
            'test_conditional_cross_entropy' : get_test_conditional_cross_entropy,
            'generalization_full_match_accuracy' : get_generalization_full_match_accuracy,
            'generalization_fine_accuracy' : get_generalization_fine_accuracy,
            'generalization_cross_entropy' : get_generalization_cross_entropy,
            'generalization_conditional_cross_entropy' : get_generalization_conditional_cross_entropy
        }
    )

if __name__ == '__main__':
    main()
