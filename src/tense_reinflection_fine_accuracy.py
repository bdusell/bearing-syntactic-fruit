import argparse
import pathlib

import torch

def load_tok_file(path):
    with path.open() as fin:
        for line in fin:
            yield line.split()

def load_tsv_file(path):
    with path.open() as fin:
        for line in fin:
            yield [s.split() for s in line.split('\t')]

def read_pos_file(path):
    with path.open() as fin:
        return dict((x.strip() for x in line.split('\t')) for line in fin)

POS_DICT = read_pos_file(pathlib.Path(__file__).parent / 'pos_tense.tsv')

def main_verb_matches(a, b):
    a_pos = sent_to_pos(a)
    if a_pos != sent_to_pos(b):
        return False
    if a_pos[2] == 'R':
        seen_verb = False
        for index, tag in enumerate(a_pos):
            if tag == 'V':
                if seen_verb:
                    verb_index = index
                    break
                else:
                    seen_verb = True
    else:
        for index, tag in enumerate(a_pos):
            if tag == 'V':
                verb_index = index
                break
    return a[verb_index] == b[verb_index]

def sent_to_pos(s):
    return [POS_DICT[w] for w in s]

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('samples', type=pathlib.Path)
    parser.add_argument('references', type=pathlib.Path)
    args = parser.parse_args()

    samples = load_tsv_file(args.samples)
    references = load_tok_file(args.references)
    result = torch.mean(torch.tensor([
        [main_verb_matches(sample, reference) for sample in sample_list]
        for sample_list, reference in zip(samples, references)
    ], dtype=torch.float))
    print(result.item())

if __name__ == '__main__':
    main()
