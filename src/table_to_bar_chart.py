import argparse
import pathlib
import re
import sys

MEAN_AND_VAR_RE = re.compile(r'^\\meanAndVar(?:Bold)?{(.*?)}{(.*?)}$')

def parse_cell(cell):
    return MEAN_AND_VAR_RE.match(cell).groups()

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--task', required=True)
    parser.add_argument('--full-output', type=pathlib.Path, required=True)
    parser.add_argument('--partial-output', type=pathlib.Path, required=True)
    args = parser.parse_args()

    line_iter = iter(sys.stdin)
    our_results = []
    for line in line_iter:
        if line == '\\midrule\n':
            break
    at_bottom = False
    for line in line_iter:
        if line == '\\midrule\n':
            break
        elif line == '\\bottomrule\n':
            at_bottom = True
            break
        cells = line.removesuffix( '\\\\\n').split(' & ')
        model = cells[0]
        our_results.append(dict(
            model=cells[0],
            full_test=float(parse_cell(cells[1])[0]),
            full_hierarchical=parse_cell(cells[2]),
            full_linear=parse_cell(cells[3]),
            partial_hierarchical=parse_cell(cells[5]),
            partial_linear=parse_cell(cells[6])
        ))
    # Only keep models with >= 90% test accuracy.
    our_results = [x for x in our_results if x['full_test'] >= 0.9]
    prior_results = []
    if not at_bottom:
        for line in line_iter:
            if line == '\\bottomrule\n':
                break
            model, line = line.split(' & ', 1)
            cells = line.removesuffix(' & \\\\\n').split(' && ')
            prior_results.append(dict(
                model=model,
                partial_hierarchical=cells[4]
            ))
    prior_results = [] # TODO remove

    def print_coordinates(accuracy_type, rule_type, fout):
        fout.write(f'''\
        \\addplot+[{rule_type}] coordinates {{
''')
        key = f'{accuracy_type}_{rule_type}'
        for m in our_results:
            mean, stddev = m[key]
            fout.write(f'({m["model"]},{mean}) +- (0,{stddev})\n')
        for m in prior_results:
            mean = m.get(key)
            if mean is not None and '--' not in mean:
                fout.write(f'({m["model"]},{mean})\n')
        fout.write('''\
        };
''')

    def print_bar_chart(accuracy_type, y_label, fout):
        fout.write(f'''\
\\begin{{tikzpicture}}
    \\begin{{axis}}[
        mybarchart,
        ylabel={{{y_label}}},
        symbolic x coords={{''')
        fout.write(','.join(x['model'] for x in our_results + prior_results))
        fout.write('''},
        title={''')
        fout.write(args.task)
        fout.write('''},
    ]
''')
        print_coordinates(accuracy_type, 'hierarchical', fout)
        print_coordinates(accuracy_type, 'linear', fout)
        fout.write('''\
    \\end{axis}
\\end{tikzpicture}
''')

    print(f'writing {args.full_output}')
    with args.full_output.open('w') as fout:
        print_bar_chart('full', 'Full Accuracy', fout)
    print(f'writing {args.partial_output}')
    with args.partial_output.open('w') as fout:
        print_bar_chart('partial', 'Partial Accuracy', fout)

if __name__ == '__main__':
    main()
