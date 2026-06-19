import argparse
import json
import pathlib

import matplotlib.pyplot as plt
import numpy

from rau.tools.torch.saver import read_logs
from rau.training.early_stopping import UpdatesWithoutImprovement

def read_snapshot(model_dir, snapshot_no):
    snapshot_dir = model_dir / str(snapshot_no)
    return float((snapshot_dir / 'fine-accuracy' / 'generalization.txt').read_text())

def read_model(model_dir, max_snapshot):
    return [read_snapshot(model_dir, i) for i in range(max_snapshot + 1)]

def read_convergence_checkpoint(model_dir):
    patience = 5
    checkpoint_no = 0
    best_checkpoint_no = 0
    early_stopping = UpdatesWithoutImprovement('min', patience)
    with read_logs(model_dir) as events:
        for event in events:
            if event.type == 'checkpoint':
                value = event.data['scores']['cross_entropy_per_token']
                is_best, should_stop = early_stopping.update(value)
                if is_best:
                    best_checkpoint_no = checkpoint_no
                if should_stop:
                    return best_checkpoint_no
                checkpoint_no += 1

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--label', action='append', default=[])
    parser.add_argument('--inputs', type=pathlib.Path, nargs='*', action='append', default=[])
    parser.add_argument('--output', type=pathlib.Path, required=True)
    parser.add_argument('--max-snapshot', type=int, required=True)
    args = parser.parse_args()

    examples_per_epoch = 100000
    examples_per_snapshot = 100000
    examples_per_checkpoint = 80000
    snapshots_per_epoch = examples_per_epoch / examples_per_snapshot
    show_individual = False

    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    ax.set_ylabel('FA')
    ax.set_xlabel('Epochs')

    x = numpy.arange(args.max_snapshot + 1) / snapshots_per_epoch
    for label, model_dirs in zip(args.label, args.inputs, strict=True):
        if show_individual:
            color = None
            for m in model_dirs:
                y = read_model(m, args.max_snapshot)
                convergence_checkpoint = read_convergence_checkpoint(m)
                convergence_epoch = convergence_checkpoint * examples_per_checkpoint / examples_per_epoch
                #line, = ax.plot(x, y, '-', label=label, color=color)
                line, = ax.plot(x, y, '-', color=color)
                color = line.get_color()
                convergence_y = numpy.interp(convergence_epoch, x, y)
                ax.plot(convergence_epoch, convergence_y, 'o', color=color)
        else:
            y_all = numpy.array([read_model(m, args.max_snapshot) for m in model_dirs])
            y_mean = numpy.mean(y_all, axis=0)
            y_std = numpy.std(y_all, axis=0, mean=y_mean)
            line, = ax.plot(x, y_mean, '-', label=label)
            color = line.get_color()
            ax.fill_between(x, y_mean - y_std, y_mean + y_std, color=color, alpha=0.2)
            convergence_checkpoint_mean = numpy.mean([read_convergence_checkpoint(m) for m in model_dirs])
            convergence_epoch_mean = convergence_checkpoint_mean * examples_per_checkpoint / examples_per_epoch
            convergence_y = numpy.interp(convergence_epoch_mean, x, y_mean)
            ax.plot(convergence_epoch_mean, convergence_y, 'o', color=color)

    ax.set_ylim(bottom=0, top=1)
    ax.set_xlim(left=0)
    ax.legend()
    plt.tight_layout()
    print(f'writing {args.output}')
    fig.savefig(args.output)

if __name__ == '__main__':
    main()
