import argparse
import pathlib

import torch

from load_util import load_tok_file, load_tsv_file

def read_pos_file(path):
    with path.open() as fin:
        return dict((x.strip() for x in line.split('\t')) for line in fin)

POS_DICT = read_pos_file(pathlib.Path(__file__).parent / 'pos_tense.tsv')

class TenseReinflectionFineAccuracy:

    def __init__(self, verb_pos):
        super().__init__()
        self.verb_pos = verb_pos

    def main_verb_matches(self, a, b):
        a_pos = sent_to_pos(a)
        if a_pos != sent_to_pos(b):
            return False
        if a_pos[2] == 'R':
            seen_verb = False
            for index, tag in enumerate(a_pos):
                if tag == self.verb_pos:
                    if seen_verb:
                        verb_index = index
                        break
                    else:
                        seen_verb = True
        else:
            for index, tag in enumerate(a_pos):
                if tag == self.verb_pos:
                    verb_index = index
                    break
        return a[verb_index] == b[verb_index]

def sent_to_pos(s):
    return [POS_DICT[w] for w in s]

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--with-do', action='store_true', default=False)
    parser.add_argument('samples', type=pathlib.Path)
    parser.add_argument('references', type=pathlib.Path)
    args = parser.parse_args()

    samples = load_tsv_file(args.samples)
    references = load_tok_file(args.references)
    metric = TenseReinflectionFineAccuracy('A' if args.with_do else 'V')
    result = torch.mean(torch.tensor([
        [metric.main_verb_matches(sample, reference) for sample in sample_list]
        for sample_list, reference in zip(samples, references)
    ], dtype=torch.float))
    print(result.item())

if __name__ == '__main__':
    main()
