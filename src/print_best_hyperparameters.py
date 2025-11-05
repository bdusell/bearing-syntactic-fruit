import argparse
import json
import pathlib
import sys

from read_model import read_data_for_multiple_trials

def to_flag(s):
    return '--' + s.replace('_', '-')

def stack_transformer_layers_to_str(layers):
    return '.'.join(map(stack_transformer_layer_to_str, layers))

def stack_transformer_layer_to_str(layer):
    if layer[0] == 'transformer':
        return str(layer[1][0])
    else:
        return stack_to_str(layer)

def stack_to_str(stack):
    name, values = stack
    return f'{name}-{"-".join(map(str, values))}'

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('models', nargs='+', type=pathlib.Path)
    args = parser.parse_args()

    trials, missing_dirs = read_data_for_multiple_trials(args.models, capture_all_events=False)
    if missing_dirs:
        print('error: missing the following models:', file=sys.stderr)
        for d in missing_dirs:
            print(d, file=sys.stderr)
        sys.exit(1)
    best_trial = min(trials, key=lambda x: x.info['train']['best_validation_scores']['cross_entropy_per_token'])
    args = []
    with (best_trial.path / 'kwargs.json').open() as fin:
        kwargs = json.load(fin)
    for name in [
        'architecture',
        'num_layers',
        'd_model',
        'num_heads',
        'feedforward_size',
        'hidden_units',
        'dropout',
        'stack_rnn_controller',
        'stack_rnn_connect_reading_to_output'
    ]:
        value = kwargs[name]
        if value is not None:
            if isinstance(value, bool):
                if value:
                    args.append(to_flag(name))
            else:
                args.append(to_flag(name))
                args.append(str(value))
    if kwargs['stack_transformer_layers'] is not None:
        args.append('--stack-transformer-layers')
        args.append(stack_transformer_layers_to_str(kwargs['stack_transformer_layers']))
    if kwargs['stack_rnn_stack'] is not None:
        args.append('--stack-rnn-stack')
        args.append(stack_to_str(kwargs['stack_rnn_stack']))
    init_scale = best_trial.info['model_info']['init_scale']
    args.append('--init-scale')
    args.append(str(init_scale))
    with (best_trial.path / 'training-loop.json').open() as fin:
        training_loop = json.load(fin)
    for name in [
        'max_tokens_per_batch',
        'optimizer',
        'initial_learning_rate',
        'label_smoothing_factor',
        'gradient_clipping_threshold',
        'early_stopping_patience',
        'learning_rate_patience',
        'learning_rate_decay_factor',
        'examples_per_checkpoint'
    ]:
        args.append(to_flag(name))
        args.append(str(training_loop[name]))
    print(' '.join(args))

if __name__ == '__main__':
    main()
