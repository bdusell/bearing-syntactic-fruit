import json
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
    if any(x is None for x in values):
        print('% warning: missing values when taking mean', file=sys.stderr)
    values = [x for x in values if x is not None]
    if values:
        return numpy.mean(values).item(), numpy.std(values).item()

def get_validation_cross_entropy(cache):
    return mean_and_std([
        t.info['train']['best_validation_scores']['cross_entropy_per_token']
        for t in cache['trials']
    ])

def get_test_full_match_accuracy(cache):
    return read_full_match_accuracy(cache, 'test')

def get_test_cross_entropy(cache):
    return read_cross_entropy(cache, 'test')

def get_test_conditional_cross_entropy(cache):
    return read_conditional_cross_entropy(cache, 'test-target')

def get_test_conditional_probability(cache):
    return read_conditional_probability(cache, 'test-target')

def get_generalization_full_match_accuracy(cache):
    return read_full_match_accuracy(cache, 'generalization')

def get_generalization_fine_accuracy(cache):
    return read_fine_accuracy(cache, 'generalization')

def get_generalization_cross_entropy(cache):
    return read_cross_entropy(cache, 'generalization')

def get_generalization_conditional_cross_entropy(cache):
    return read_conditional_cross_entropy(cache, 'generalization-target')

def get_generalization_conditional_probability(cache):
    return read_conditional_probability(cache, 'generalization-target')

def get_wrong_generalization_full_match_accuracy(cache):
    return read_full_match_accuracy(cache, 'generalization-wrong')

def get_wrong_generalization_fine_accuracy(cache):
    return read_fine_accuracy(cache, 'generalization-wrong')

def get_wrong_generalization_conditional_cross_entropy(cache):
    return read_cross_entropy(cache, 'generalization-wrong-target')

def get_generalization_log_ratio(cache):
    return mean_and_std([
        read_txt(t, 'probability', 'generalization-ratio')
        for t in cache['trials']
    ])

def read_txt(trial, subdir, dataset):
    file_path = trial.path / 'eval' / subdir / f'{dataset}.txt'
    try:
        text = file_path.read_text()
    except FileNotFoundError:
        print(f'% warning: file not found: {file_path}', file=sys.stderr)
        return None
    try:
        result = float(text)
    except ValueError:
        print(f'% warning: not parsable: {file_path}', file=sys.stderr)
        return None
    return result

def read_json(trial, subdir, dataset):
    file_path = trial.path / 'eval' / subdir / f'{dataset}.json'
    try:
        with file_path.open() as fin:
            return json.load(fin)
    except FileNotFoundError:
        print(f'% warning: file not found: {file_path}', file=sys.stderr)
        return None

def read_json_attr(trial, subdir, dataset, key):
    data = read_json(trial, subdir, dataset)
    if data:
        return data[key]

def read_full_match_accuracy(cache, dataset):
    return mean_and_std([
        read_txt(t, 'greedy', dataset)
        for t in cache['trials']
    ])

def read_fine_accuracy(cache, dataset):
    return mean_and_std([
        read_txt(t, 'fine-accuracy', dataset)
        for t in cache['trials']
    ])

def read_cross_entropy(cache, dataset):
    return mean_and_std([
        read_txt(t, 'cross-entropy', dataset)
        for t in cache['trials']
    ])

def read_conditional_probability(cache, dataset):
    return mean_and_std([
        read_json_attr(t, 'probability', dataset, 'mean_sequence_probability')
        for t in cache['trials']
    ])

def read_conditional_cross_entropy(cache, dataset):
    return mean_and_std([
        read_json_attr(t, 'probability', dataset, 'cross_entropy_per_token')
        for t in cache['trials']
    ])

def main():
    places = (3, 2)
    col_format = format_mean_and_variance(places=(3, 2))
    run_main(
        header=r'''
& \multicolumn{2}{c}{Test} & \multicolumn{6}{c}{Generalization} \\
\cmidrule(lr){2-3} \cmidrule(lr){4-9}
'''.strip(),
        columns=[
            Column('Architecture', 'l', 'label', format_text()),
            Column('CP $\\uparrow$', 'S', 'test_conditional_probability', col_format, bold_max=True),
            Column('CP $\\uparrow$', 'S', 'generalization_conditional_probability', col_format, bold_max=True),
            Column('CCE $\\downarrow$', 'S', 'generalization_conditional_cross_entropy', col_format, bold_min=True),
            Column('FA $\\uparrow$', 'S', 'generalization_fine_accuracy', col_format, bold_max=True),
            Column('Log Ratio $\\uparrow$', 'S', 'generalization_log_ratio', col_format, bold_max=True)
        ],
        callbacks={
            'validation_cross_entropy' : get_validation_cross_entropy,
            'test_full_match_accuracy' : get_test_full_match_accuracy,
            'test_cross_entropy' : get_test_cross_entropy,
            'test_conditional_cross_entropy' : get_test_conditional_cross_entropy,
            'test_conditional_probability' : get_test_conditional_probability,
            'generalization_full_match_accuracy' : get_generalization_full_match_accuracy,
            'generalization_fine_accuracy' : get_generalization_fine_accuracy,
            'generalization_cross_entropy' : get_generalization_cross_entropy,
            'generalization_conditional_cross_entropy' : get_generalization_conditional_cross_entropy,
            'generalization_conditional_probability' : get_generalization_conditional_probability,
            'wrong_generalization_full_match_accuracy' : get_wrong_generalization_full_match_accuracy,
            'wrong_generalization_fine_accuracy' : get_wrong_generalization_fine_accuracy,
            'wrong_generalization_conditional_cross_entropy' : get_wrong_generalization_conditional_cross_entropy,
            'generalization_log_ratio' : get_generalization_log_ratio
        }
    )

if __name__ == '__main__':
    main()
